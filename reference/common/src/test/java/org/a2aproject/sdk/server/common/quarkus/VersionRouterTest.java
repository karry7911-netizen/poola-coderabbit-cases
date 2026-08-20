package org.a2aproject.sdk.server.common.quarkus;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.vertx.core.http.HttpServerRequest;
import io.vertx.ext.web.RoutingContext;
import org.a2aproject.sdk.common.A2AHeaders;
import org.junit.jupiter.api.Test;

class VersionRouterTest {

    @Test
    void missingHeaderDefaultsTo03() {
        RoutingContext rc = mockRc(null, null);
        assertEquals(VersionRouter.VERSION_0_3, VersionRouter.resolveVersion(rc));
    }

    @Test
    void emptyHeaderDefaultsTo03() {
        RoutingContext rc = mockRc("", null);
        assertEquals(VersionRouter.VERSION_0_3, VersionRouter.resolveVersion(rc));
    }

    @Test
    void explicitV10() {
        RoutingContext rc = mockRc("1.0", null);
        assertEquals(VersionRouter.VERSION_1_0, VersionRouter.resolveVersion(rc));
    }

    @Test
    void explicitV03() {
        RoutingContext rc = mockRc("0.3", null);
        assertEquals(VersionRouter.VERSION_0_3, VersionRouter.resolveVersion(rc));
    }

    @Test
    void queryParamFallback() {
        RoutingContext rc = mockRc(null, "1.0");
        assertEquals(VersionRouter.VERSION_1_0, VersionRouter.resolveVersion(rc));
    }

    @Test
    void headerTakesPrecedenceOverQueryParam() {
        RoutingContext rc = mockRc("0.3", "1.0");
        assertEquals(VersionRouter.VERSION_0_3, VersionRouter.resolveVersion(rc));
    }

    @Test
    void unsupportedVersionPassedThrough() {
        RoutingContext rc = mockRc("2.0", null);
        assertEquals("2.0", VersionRouter.resolveVersion(rc));
    }

    private RoutingContext mockRc(String headerValue, String queryParamValue) {
        RoutingContext rc = mock(RoutingContext.class);
        HttpServerRequest request = mock(HttpServerRequest.class);
        when(rc.request()).thenReturn(request);
        when(request.getHeader(A2AHeaders.A2A_VERSION)).thenReturn(headerValue);
        when(request.getParam(A2AHeaders.A2A_VERSION)).thenReturn(queryParamValue);
        return rc;
    }
}
