
# Using spin

In order to test spin we need multiple components:

- cluster
- spin operator and executor (installed in this dir)
- nginx for hpa (and it also will take care of routing in that case)
- containerd spin shim (installed in this dir)

Once the app is deployed, it should be available like so (regardless of native
or spintainer deployment):

```sh
curl -H "Host: nuhakala.com" $(tools.sh ip)
```


# Containerized apps

Cannot use spintainer executor, it cannot pull images from my local registry.
Hence I specify the deployment by hand.

# Kubeedge

Should work out of the box with kubeedge, assuming edgemesh is installed. Edge
gateway not needed, just install nginx and the virtualserver should do route the
requests correctly.
