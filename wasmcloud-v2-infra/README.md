
# Wasmcloud

Because there are no ready-built artifacts for the RC versions, you need to
clone the wash repo `wasmcloud/wash` and build the rc6 (or rc7) components
yourself and push them to local registry. The images are then defined in the
local helm values file.

In addition, to be able to run **workloads from local registry**, you need to
add a flag `--allow-insecure-registries` to the runtime deployment template in
the helm chart. This is already added to the charts.

# No autoscaling

Adding `/scale` subresource allowed to scale the workloads with `kubectl scale`,
but apparently [see here](https://github.com/kedacore/keda/issues/5898) `/scale`
needs to be implemented correctly for the hpa to work, and since keda is relying
on HPA, the autoscaling does not work.

# Kubeedge

Kubeedge requires service mesh. Using the wasmcloud gateway with that service
mesh did not work: wasmCloud runtime-gateway tries to route the http requests
using IP address of pods, but that does not work with the service mesh. It would
neet to route using domain names in order for the service mesh to work.

Luckily we can leverage the service mesh gateway with native K8s routing. We
have a service for the wasmCloud hosts, and then the Edgemesh gateway can route
requests to the hosts correctly. Only caveat is that it will load balance
between the hosts without taking into account the wasmCloud workloads: if one
workload is deployed and 10 hosts are available, 9/10 requests will land on
empty host and won't return any response.
