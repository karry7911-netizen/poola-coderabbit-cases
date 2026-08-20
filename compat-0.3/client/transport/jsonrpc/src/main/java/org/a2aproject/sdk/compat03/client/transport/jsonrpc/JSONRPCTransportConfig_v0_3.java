package org.a2aproject.sdk.compat03.client.transport.jsonrpc;

import org.a2aproject.sdk.client.http.A2AHttpClient;
import org.a2aproject.sdk.compat03.client.transport.spi.ClientTransportConfig_v0_3;

public class JSONRPCTransportConfig_v0_3 extends ClientTransportConfig_v0_3<JSONRPCTransport_v0_3> {

    private final A2AHttpClient httpClient;

    public JSONRPCTransportConfig_v0_3() {
        this.httpClient = null;
    }

    public JSONRPCTransportConfig_v0_3(A2AHttpClient httpClient) {
        this.httpClient = httpClient;
    }

    public A2AHttpClient getHttpClient() {
        return httpClient;
    }
}
