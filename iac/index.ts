import * as pulumi from "@pulumi/pulumi";
import * as k8s from "@pulumi/kubernetes";
import { getAppConfig } from "./libraries/configuration";

const APP_ID = "agent-hub";
const ENV_PREFIX = "AGENT_HUB_";
const config = new pulumi.Config(APP_ID);

const nsControlPlane = new k8s.core.v1.Namespace("ns-agents-control-plane", {
  metadata: { name: "agents-control-plane" },
});

const appConfig = getAppConfig(
	config, ENV_PREFIX, pulumi.runtime.allConfig(), config.name
);

const secret = new k8s.core.v1.Secret(`${APP_ID}-secrets`, {
  metadata: { namespace: nsControlPlane.metadata.name },
  stringData: appConfig.secrets,
});

const configMap = new k8s.core.v1.ConfigMap(`${APP_ID}-config`, {
  metadata: { namespace: nsControlPlane.metadata.name },
  data: appConfig.plainConfig,
});

// 3. Deployment
const appLabels = { app: APP_ID };

const deployment = new k8s.apps.v1.Deployment(`${APP_ID}-deployment`, {
  metadata: {
    namespace: nsControlPlane.metadata.name,
    labels: appLabels,
  },
  spec: {
    replicas: 1,
    selector: { matchLabels: appLabels },
    template: {
      metadata: { labels: appLabels },
      spec: {
        containers: [{
          name: APP_ID,
          image: `ghcr.io/compilercomplied/${APP_ID}:latest`,
          imagePullPolicy: "Always",
          ports: [{ containerPort: 8000 }],
          envFrom: [
            { secretRef: { name: secret.metadata.name } },
            { configMapRef: { name: configMap.metadata.name } },
          ],
          readinessProbe: {
            httpGet: {
              path: "/health",
              port: 8000,
            },
            initialDelaySeconds: 5,
            periodSeconds: 10,
          },
          livenessProbe: {
            httpGet: {
              path: "/health",
              port: 8000,
            },
            initialDelaySeconds: 15,
            periodSeconds: 20,
          },
        }],
      },
    },
  },
});

// 4. Service
const service = new k8s.core.v1.Service(`${APP_ID}-svc`, {
  metadata: {
    namespace: nsControlPlane.metadata.name,
    name: APP_ID,
  },
  spec: {
    selector: appLabels,
    ports: [{ port: 80, targetPort: 8000 }],
    type: "ClusterIP",
  },
});

// Export the internal URL
export const internalUrl = pulumi.interpolate`http://${service.metadata.name}.${nsControlPlane.metadata.name}.svc.cluster.local`;
