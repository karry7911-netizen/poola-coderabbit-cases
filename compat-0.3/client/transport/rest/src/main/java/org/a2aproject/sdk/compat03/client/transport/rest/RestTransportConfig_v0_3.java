package org.a2aproject.sdk.compat03.client.transport.rest;

import org.a2aproject.sdk.client.http.A2AHttpClient;
import org.a2aproject.sdk.compat03.client.transport.spi.ClientTransportConfig_v0_3;
import org.jspecify.annotations.Nullable;

public class RestTransportConfig_v0_3 extends ClientTransportConfig_v0_3<RestTransport_v0_3> {

    private final @Nullable A2AHttpClient httpClient;

    public RestTransportConfig_v0_3() {
        this.httpClient = null;
    }

    public RestTransportConfig_v0_3(A2AHttpClient httpClient) {
        this.httpClient = httpClient;
    }

    public @Nullable A2AHttpClient getHttpClient() {
        return httpClient;
    }
}
