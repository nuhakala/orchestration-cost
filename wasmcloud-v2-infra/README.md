
# Wasmcloud

Because there are no ready-built artifacts for the RC versions, you need to
clone the wash repo `wasmcloud/wash` and build the rc6 (or rc7) components
yourself and push them to local registry. The images are then defined in the
local helm values file.

In addition, to be able to run **workloads** from local registry, you need to
add a flag `--allow-insecure-registries` to the runtime deployment template in
the helm chart. This is already added to the charts.

# No autoscaling

Adding `/scale` subresource allowed to scale the workloads with `kubectl scale`,
but apparently [see here](https://github.com/kedacore/keda/issues/5898) `/scale`
needs to be implemented correctly for the hpa to work, and since keda is relying
on HPA, the autoscaling does not work.

# Kubeedge

Kubeedge requires service mesh. Using the wasmcloud gateway with that service
mesh did not work, but luckily my workload is such that I think I can safely use
k8s services for load-balancing. Hence just forward the requests from edge
gateway directly to the hostgroup svc and it should work.

This is also fine because wasmcloud does not support autoscaling, so this kind
of routing is enough for static deployments.
