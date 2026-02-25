
# Images

When running kubeedge, we need four images: cloudcore, edgecore, installation
package and iptables-manager. These four need to be built and pushed to the
registry:

```sh
# Make pushes the image also
IMAGE_REPO_NAME="192.168.68.54:5000" make crossbuildimage WHAT=cloudcore
IMAGE_REPO_NAME="192.168.68.54:5000" make crossbuildimage WHAT=edgecore
IMAGE_REPO_NAME="192.168.68.54:5000" make crossbuildimage WHAT=iptables-manager
IMAGE_REPO_NAME="192.168.68.54:5000" make crossbuildimage WHAT=installation-package
```

When having these images in local registry, we can install kubeedge with keadm
by giving the local registry to it.

Note that we need to tag and put the installation-package to
`10.164.178.1:5000/kubeedge/installation-package:v1.22.0`. If we leave
the kubeedge namespace out, keadm tries to pull the image from docker.io. No
clue why.

## Why this way?

Latest release 1.22 does not support K8s 1.32, I guess there is something
broken, so that is why the master branch needs to be used.

# How does kubeedge work

So the cloudcore needs access to kube api server. Typically it runs on the same
machine as the control plane.

On edge node, we have only container runtime and edgecore running. Edgecore
conflicts with kubelet so we are not supposed to have a k8s cluster at edge
node: edgecore takes care of containers there.

Edgecore does not have kubelet, we need to expose kube api there (tbh not sure
if it is needed, could test also without) [instructions](https://edgemesh.netlify.app/guide/edge-kube-api)

Edgecore then communicates with cloud core, which communicates with k8s.

Note, that kubeedge does not have connection between the edge containers by
default (tried it) hence we need to have edgemesh. Edgemesh enables us to expose the
services. I use nginx ingress conttroller with virtualserver to access them,
other option is to use istio gateway, but I need the nginx metrics.

# Running Spin

[Edgecore does not support runtimeclass](https://github.com/kubeedge/kubeedge/issues/4416)
hence only containerized workloads are possible.
