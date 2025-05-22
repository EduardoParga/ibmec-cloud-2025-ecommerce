package br.edu.ibmec.cloud.ecommerce_cloud.configuration;

// Removido temporariamente o uso das anotações Spring para evitar erro de contexto
// import org.springframework.boot.context.properties.ConfigurationProperties;
// import lombok.Getter;
// import lombok.Setter;

// @Getter
// @Setter
// @ConfigurationProperties(prefix = "azure.cosmos")
public class CosmosProperties {

    private String uri;
    private String key;
    private String database;
    private boolean queryMetricsEnabled;
    private boolean responseDiagnosticsEnabled;

    // Getters e setters adicionados manualmente (já que o @Getter/@Setter estão comentados)
    public String getUri() {
        return uri;
    }

    public void setUri(String uri) {
        this.uri = uri;
    }

    public String getKey() {
        return key;
    }

    public void setKey(String key) {
        this.key = key;
    }

    public String getDatabase() {
        return database;
    }

    public void setDatabase(String database) {
        this.database = database;
    }

    public boolean isQueryMetricsEnabled() {
        return queryMetricsEnabled;
    }

    public void setQueryMetricsEnabled(boolean queryMetricsEnabled) {
        this.queryMetricsEnabled = queryMetricsEnabled;
    }

    public boolean isResponseDiagnosticsEnabled() {
        return responseDiagnosticsEnabled;
    }

    public void setResponseDiagnosticsEnabled(boolean responseDiagnosticsEnabled) {
        this.responseDiagnosticsEnabled = responseDiagnosticsEnabled;
    }
}
