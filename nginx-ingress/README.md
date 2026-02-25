
In order to use requests-per-second metric, we need to first create/collect that
metrics somehow, as it is not core kubernetes metric. We need

1. prometheus server to collect and serve the metric
2. Ingress controller which creates metrics endpoint and serves the metrics, so
   that prometheus can collect them
3. Prometheus adapters, so that the metrics can be transferred from prometheus
   to kubernetes. Prometheus itself is just metrics collection tool usually used
   to visualize the data.

Instructions

- [How to install nginx controller](https://docs.nginx.com/nginx-ingress-controller/install/helm/open-source/)
- [How to enable prometheus with nginx controller](https://docs.nginx.com/nginx-ingress-controller/logging-and-monitoring/prometheus/)
- [How to set up prometheus adapter](https://github.com/kubernetes-sigs/prometheus-adapter/blob/master/docs/walkthrough.md)
- [How to install prometheus operator](https://prometheus-operator.dev/docs/getting-started/installation/)
- [How to create prometheus server](https://prometheus-operator.dev/docs/platform/platform-guide/)

Check that deployment is successful:

``` sh
kubectl get --raw /apis/external.metrics.k8s.io/v1beta1
kubectl get --raw /apis/external.metrics.k8s.io/v1beta1/namespaces/bar/http_requests_per_second
```

Note that we need to always supply the namespace. But when using external
metrics, we can give `namespaced: false` to prometheus adapter config, and it
actually ignores the namespace. This is not visible really anyway other than we
can give nonexistent namespaces to the query and it still works. NOTE: when
listing the resources with the above command, it still says that `namespaced:
true` but it is not correct.

**NOTE when curling** we need to give domain to the virtualserver/ingress when
deploying the application, and we need to give the domain in host header when
curling. **IMPORTANT THING TO NOTE IS THAT THE DOMAIN TO GIVE WHEN CURLING IS
THE SAME WE HAVE DEFINED!**

# Prometheus adapter

Prometheus adapter is version 0.12.0. The source code was downloaded from github
and everything else than the deploy manifests were deleted. Prometheus version
is 3.9.1 and nginx ingress version 5.3.1

To make it work (from fresh install):

- edit the deployment to have correct number of adapter replicas
- edit the deployment to point to correct prometheus service and use http (not
  https)
- edit the configmap to have proper configuration
