# infra/terraform/main.tf

provider "aws" {
  region = "ap-northeast-2"
}

# ==========================================
# 1. 권한 및 보안 (IAM Role & Policy)
# ==========================================

# AI Worker가 사용할 역할 (Role)
resource "aws_iam_role" "ai_worker_role" {
  name = "leh-ai-worker-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

# AI Worker가 S3, DynamoDB, CloudWatch를 쓸 수 있는 권한 (Policy)
resource "aws_iam_role_policy" "ai_worker_policy" {
  name = "leh-ai-worker-policy"
  role = aws_iam_role.ai_worker_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:GetItem",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

# ==========================================
# 2. 저장소 (Storage & Database)
# ==========================================

# S3 버킷 (증거 원본)
resource "aws_s3_bucket" "evidence_bucket" {
  bucket = "leh-evidence-prod-v2" # 유니크한 이름으로 변경 필요
}

# 정적 프론트엔드 호스팅 버킷 (CloudFront 배포 대상)
resource "aws_s3_bucket" "frontend_site" {
  bucket = "leh-frontend-static-prod"

  tags = {
    Purpose = "nextjs-static-site"
  }
}

# SPA fallback을 위해 index.html을 인덱스/에러 문서로 지정
resource "aws_s3_bucket_website_configuration" "frontend_site" {
  bucket = aws_s3_bucket.frontend_site.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}

# CloudFront에서만 읽을 수 있도록 퍼블릭 정책을 적용 (정적 사이트)
resource "aws_s3_bucket_policy" "frontend_site" {
  bucket = aws_s3_bucket.frontend_site.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowCloudFrontAccess"
        Effect    = "Allow"
        Principal = "*"
        Action    = ["s3:GetObject"]
        Resource  = ["${aws_s3_bucket.frontend_site.arn}/*"]
      }
    ]
  })
}

# CloudFront 배포 (SPA fallback용 커스텀 에러 응답 포함)
resource "aws_cloudfront_distribution" "frontend" {
  enabled             = true
  default_root_object = "index.html"

  origins {
    domain_name = aws_s3_bucket_website_configuration.frontend_site.website_endpoint
    origin_id   = "s3-frontend-site"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "s3-frontend-site"
    viewer_protocol_policy = "redirect-to-https"
    compress = true

    forwarded_values {
      query_string = true
      cookies {
        forward = "none"
      }
    }
  }

  price_class = "PriceClass_100"

  custom_error_response {
    error_code            = 404
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 0
  }

  custom_error_response {
    error_code            = 403
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 0
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

# DynamoDB (증거 메타데이터)
resource "aws_dynamodb_table" "evidence_meta" {
  name         = "leh-evidence-prod"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "case_id"
  range_key    = "evidence_id"

  attribute {
    name = "case_id"
    type = "S"
  }
  attribute {
    name = "evidence_id"
    type = "S"
  }
}

# ECR 리포지토리 (Docker 이미지 저장소)
resource "aws_ecr_repository" "backend_repo" {
  name = "leh-backend"
}

resource "aws_ecr_repository" "ai_worker_repo" {
  name = "leh-ai-worker"
}

# ==========================================
# 3. 컴퓨팅 (Compute - Lambda)
# ==========================================

# AI Worker Lambda 함수 정의
# (주의: 최초 배포 전에는 더미 이미지가 필요할 수 있음)
resource "aws_lambda_function" "ai_worker" {
  function_name = "leh-ai-worker"
  role          = aws_iam_role.ai_worker_role.arn
  package_type  = "Image"
  
  # ECR에 이미지가 없으면 terraform apply가 실패할 수 있음.
  # 초기엔 'hello-world' 같은 더미 이미지를 지정하거나,
  # GitHub Actions가 먼저 이미지를 푸시한 후 Terraform을 돌려야 함.
  image_uri     = "${aws_ecr_repository.ai_worker_repo.repository_url}:latest"
  
  timeout       = 300  # 5분 (AI 분석 시간 고려)
  memory_size   = 1024 # 1GB (이미지 처리 고려)

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.evidence_meta.name
      # OPENAI_API_KEY 등은 AWS Console에서 수동 설정하거나 Secrets Manager 연동 권장
    }
  }
}

# ==========================================
# 4. 이벤트 트리거 (Event Trigger)
# ==========================================

# S3 업로드 시 -> Lambda 자동 실행 권한 부여
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ai_worker.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.evidence_bucket.arn
}

# S3 버킷 알림 설정 (실제 트리거 연결)
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.evidence_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.ai_worker.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "cases/"  # cases 폴더 내 파일만 처리
  }

  depends_on = [aws_lambda_permission.allow_s3]
}
