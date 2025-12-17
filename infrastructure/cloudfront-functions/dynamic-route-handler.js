/**
 * CloudFront Function: Dynamic Route Handler
 *
 * This function handles dynamic routes for Next.js static export.
 * When a request comes in for a path like /lawyer/cases/{dynamic-id}/,
 * it rewrites the origin path to serve a pre-rendered fallback page.
 * The client-side JavaScript then reads the actual URL to get the case ID.
 *
 * Usage:
 * 1. Create a CloudFront Function with this code
 * 2. Associate it with the CloudFront distribution as a "viewer request" function
 *
 * Pre-rendered IDs (from generateStaticParams):
 * - 1, 2, 3, test-case-001, test-case-empty
 */

// Pre-rendered case IDs that have actual HTML files in S3
var PRERENDERED_IDS = ['1', '2', '3', 'test-case-001', 'test-case-empty'];

// Fallback ID to use when serving dynamic routes
var FALLBACK_ID = '1';

/**
 * Handler function for CloudFront viewer-request event
 */
function handler(event) {
    var request = event.request;
    var uri = request.uri;

    // Pattern: /{role}/cases/{id}/ or /{role}/cases/{id}/{section}/
    // Roles: lawyer, client, detective, staff
    var caseDetailPattern = /^\/(lawyer|client|detective|staff)\/cases\/([^\/]+)(\/(?:procedure|assets|relations|relationship)?)?\/?(index\.html)?$/;
    var match = uri.match(caseDetailPattern);

    if (match) {
        var role = match[1];
        var caseId = match[2];
        var section = match[3] || '';
        var indexHtml = match[4] || '';

        // Check if this is a pre-rendered ID
        var isPrerendered = false;
        for (var i = 0; i < PRERENDERED_IDS.length; i++) {
            if (PRERENDERED_IDS[i] === caseId) {
                isPrerendered = true;
                break;
            }
        }

        // If not pre-rendered, rewrite to fallback
        if (!isPrerendered) {
            // Build the new URI with the fallback ID
            var newUri = '/' + role + '/cases/' + FALLBACK_ID + section;

            // Ensure trailing slash
            if (!newUri.endsWith('/')) {
                newUri += '/';
            }

            // Add index.html for S3 compatibility
            newUri += 'index.html';

            request.uri = newUri;
        } else {
            // For pre-rendered IDs, ensure the URI ends with /index.html
            if (!uri.endsWith('/index.html')) {
                if (uri.endsWith('/')) {
                    request.uri = uri + 'index.html';
                } else {
                    request.uri = uri + '/index.html';
                }
            }
        }
    }

    return request;
}
