# ai_worker/Dockerfile
# AWS Lambda 배포용 (Container Image)

FROM public.ecr.aws/lambda/python:3.12

# System dependencies for OCR and media processing
RUN dnf install -y \
    tesseract \
    tesseract-langpack-kor \
    ffmpeg \
    && dnf clean all

# Set working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY handler.py .

# Lambda handler
CMD [ "handler.handle" ]
