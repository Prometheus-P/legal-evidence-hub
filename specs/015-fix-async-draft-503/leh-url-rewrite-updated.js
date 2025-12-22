function handler(event) {
    var request = event.request;
    var uri = request.uri;

    // Skip API requests - pass through to API Gateway origin
    if (uri.startsWith('/api/')) {
        return request;
    }

    // Skip Next.js static assets
    if (uri.startsWith('/_next/')) {
        return request;
    }

    // Skip files with extensions (images, css, js, etc.)
    if (uri.includes('.')) {
        return request;
    }

    // Known static routes that exist in S3 as pre-rendered pages
    // These paths have corresponding index.html files in S3
    var staticRoutes = [
        '/',
        '/auth/login',
        '/auth/register',
        '/auth/forgot-password',
        '/lawyer',
        '/lawyer/cases',
        '/lawyer/clients',
        '/lawyer/investigators',
        '/lawyer/calendar',
        '/lawyer/messages',
        '/lawyer/billing',
        '/staff',
        '/staff/cases',
        '/staff/progress',
        '/admin',
        '/settings'
    ];

    // Normalize URI (remove trailing slash for comparison)
    var normalizedUri = uri.endsWith('/') && uri !== '/' ? uri.slice(0, -1) : uri;

    // Check if this is a known static route
    var isStaticRoute = staticRoutes.indexOf(normalizedUri) !== -1;

    if (isStaticRoute) {
        // For static routes, append /index.html
        if (!uri.endsWith('/')) {
            uri = uri + '/';
        }
        request.uri = uri + 'index.html';
    } else {
        // For dynamic routes (e.g., /lawyer/cases/case_123), serve root index.html
        // Next.js client-side routing will handle the actual navigation
        request.uri = '/index.html';
    }

    return request;
}
