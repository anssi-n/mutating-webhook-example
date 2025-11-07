### Create a namespace and a service for mutating webhook server

```
kubectl create namespace mutatingwebhook
```

```
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  labels:
    app: mutatingwebhook
  name: mutatingwebhook
  namespace: mutatingwebhook
spec:
  ports:
  - name: https
    port: 443
    protocol: TCP
    targetPort: 8443
  selector:
    app: mutatingwebhook
  type: ClusterIP
EOF
```

### Create Server Certificates

Create the key and a certificate signing request for the mutating webhook server. Note namespace and service names in DNS entries.

```
openssl genrsa -out mutating-webhook-server.key 2048
openssl req -new -key mutating-webhook-server.key -subj "/CN=system:node:mutatingwebhook/O=system:nodes" -addext "subjectAltName = DNS:mutatingwebhook.mutatingwebhook.svc.cluster.local,DNS:mutatingwebhook.mutatingwebhook.svc,DNS:mutatingwebhook.mutatingwebhook.pod.cluster.local" -out mutating-webhook-server.csr
```

```
export SIGNING_REQUEST=$(cat webhook-server.csr | base64 | tr -d "\n")
```

```
cat <<EOF | kubectl apply -f -
apiVersion: certificates.k8s.io/v1
kind: CertificateSigningRequest
metadata:
  name: mutating-webhook-server
spec:
  request: $SIGNING_REQUEST
  signerName: kubernetes.io/kubelet-serving
  expirationSeconds: 864000  # ten days
  usages:
  - digital signature
  - key encipherment
  - server auth
EOF
```

Approve the CSR and get signed certificate to a file.

```
kubectl get csr
kubectl certificate approve mutating-webhook-server
kubectl get csr mutating-webhook-server  -o=jsonpath={.status.certificate} | base64 --decode > mutating-webhook-server.crt
```

### Create a secret with the certificates for the server

```
kubectl create secret tls mutating-webhook-server --cert=mutating-webhook-server.crt --key=mutating-webhook-server.key -n mutatingwebhook
```

### Deploy the mutating webhook server in mutatingwebhook namespace

```
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: mutatingwebhook
  name: mutatingwebhook
  namespace: mutatingwebhook
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mutatingwebhook
  template:
    metadata:
      labels:
        app: mutatingwebhook
    spec:
      volumes:
        - name: cert
          secret:
            secretName: mutating-webhook-server
            items:
              - key: tls.crt
                path: mutating-webhook-server.crt
        - name: key
          secret:
            secretName: mutating-webhook-server
            items:
              - key: tls.key
                path: mutating-webhook-server.key
      containers:
      - image: bobfleming/mutating-webhook-example:0.1.0
        name: mutatingwebhook
        ports:
        - containerPort: 8443

        env:
          - name: SSL_CERTFILE
            value: /etc/ssl/certs/mutating-webhook-server.crt
          - name: SSL_KEYFILE
            value: /etc/ssl/private/mutating-webhook-server.key

        volumeMounts:
          - name: cert
            readOnly: true
            mountPath: /etc/ssl/certs/
          - name: key
            readOnly: true
            mountPath: /etc/ssl/private/
EOF
```

### Deploy the mutating webhook configuration using the mutating webhook server

Webhook is applied when pods are created in namespace with label webhook: enabled. Add base64 encoded CA cert created previously to caBundle field.

```
cat <<EOF | kubectl apply -f -
apiVersion: admissionregistration.k8s.io/v1
kind: MutatingWebhookConfiguration
metadata:
  name: "mymutatingwebhook.example.com"
webhooks:
- name: "mymutatingwebhook.example.com"
  namespaceSelector:
    matchLabels:
      webhook: enabled
  rules:
  - apiGroups:   [""]
    apiVersions: ["v1"]
    operations:  ["CREATE"]
    resources:   ["pods"]
  clientConfig:
    service:
      namespace: "mutatingwebhook"
      name: "mutatingwebhook"
      path: "/webhook"
    caBundle: <ADD CA CERT HERE>
  admissionReviewVersions: ["v1", "v1beta1"]
  sideEffects: None
  timeoutSeconds: 5
EOF
```

### Create a namespace for app pods and add label to enabele the webhook

```
kubectl create namespace mutatingwebhookdemo
kubectl label namespace mutatingwebhookdemo webhook=enabled
```

### Run pod in app namespace and check that new labels are added by the mutating webhook server

```
kubectl run nginx --image nginx -n mutatingwebhookdemo
kubectl get pods nginx -n mutatingwebhookdemo -oyaml
```
