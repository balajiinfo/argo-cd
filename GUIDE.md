# Complete Argo CD Hands-On Guide
## Deploy a Real App on Windows with Minikube

---

## YOUR REPO STRUCTURE
```
myapp-gitops/          ← Your GitHub repo
├── app/
│   ├── app.py         ← Flask application code
│   ├── requirements.txt
│   └── Dockerfile
└── k8s/
    ├── deployment.yaml
    ├── service.yaml
    └── argocd-app.yaml
```

---

## PHASE 1 — Install Tools (Do This Once)

### Step 1.1 — Install Docker Desktop
- Download: https://www.docker.com/products/docker-desktop/
- Install and open Docker Desktop
- Go to Settings → Resources → set RAM to 4 GB, CPU to 2
- Make sure Docker is running (whale icon in taskbar)

### Step 1.2 — Install kubectl
Open PowerShell as Administrator and run:
```powershell
winget install Kubernetes.kubectl
```
Verify:
```powershell
kubectl version --client
```

### Step 1.3 — Install Minikube
```powershell
winget install Kubernetes.minikube
```
Verify:
```powershell
minikube version
```

### Step 1.4 — Start Minikube
```powershell
minikube start --driver=docker --memory=4096 --cpus=2
```
Wait 2-3 minutes. Then verify:
```powershell
kubectl get nodes
# Should show:  minikube   Ready
```

---

## PHASE 2 — GitHub Setup

### Step 2.1 — Create GitHub Repo
1. Go to https://github.com/new
2. Name it: `myapp-gitops`
3. Make it Public (Argo CD needs to read it)
4. Click "Create repository"

### Step 2.2 — Push Your Code
In PowerShell, go to where you extracted the project folder:
```powershell
cd path\to\myapp

git init
git add .
git commit -m "Initial commit - Flask todo app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/myapp-gitops.git
git push -u origin main
```

---

## PHASE 3 — Docker Hub Setup

### Step 3.1 — Create Docker Hub Account
- Go to https://hub.docker.com and sign up (free)
- Your username will be used in the image name

### Step 3.2 — Login to Docker Hub (on your PC)
```powershell
docker login
# Enter your Docker Hub username and password
```

### Step 3.3 — Build and Push the Docker Image
```powershell
# Go into the app folder
cd path\to\myapp\app

# Build the image  (replace YOUR_USERNAME with your Docker Hub username)
docker build -t YOUR_USERNAME/myapp:v1 .

# Push to Docker Hub
docker push YOUR_USERNAME/myapp:v1
```

Check it on Docker Hub: https://hub.docker.com/r/YOUR_USERNAME/myapp

### Step 3.4 — Update deployment.yaml
Open k8s/deployment.yaml and change this line:
```yaml
image: YOUR_DOCKERHUB_USERNAME/myapp:v1
```
To:
```yaml
image: john123/myapp:v1    # ← your actual Docker Hub username
```

Also update k8s/argocd-app.yaml:
```yaml
repoURL: https://github.com/YOUR_USERNAME/myapp-gitops
```

Then commit and push the changes:
```powershell
git add k8s/deployment.yaml k8s/argocd-app.yaml
git commit -m "Update image name and repo URL"
git push
```

---

## PHASE 4 — Install Argo CD

### Step 4.1 — Create Namespace and Install
```powershell
kubectl create namespace argocd

kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

### Step 4.2 — Wait for Pods to Be Ready
```powershell
kubectl get pods -n argocd -w
```
Wait until ALL pods show `Running`. Press Ctrl+C when done.
This can take 3-5 minutes.

### Step 4.3 — Open Argo CD UI
In a NEW PowerShell window (keep it open while using Argo CD):
```powershell
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

Now open your browser: https://localhost:8080
(Click "Advanced" → "Proceed" if you see a certificate warning)

### Step 4.4 — Get Admin Password
In another PowerShell window:
```powershell
kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath="{.data.password}" | ForEach-Object { [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($_)) }
```
Copy this password.

Login to Argo CD UI:
- Username: `admin`
- Password: (paste the password you just got)

---

## PHASE 5 — Deploy Your App with Argo CD

### Step 5.1 — Register Your App
```powershell
kubectl apply -f k8s/argocd-app.yaml
```

### Step 5.2 — Watch in the UI
Go to https://localhost:8080
You should see your app `myapp` appear.
Click on it → you'll see the pods, deployment, and service being created.

It will show:
- Status: Synced ✅
- Health: Healthy 💚

### Step 5.3 — Access Your Running App
```powershell
minikube service myapp-service --url
```
Open the URL it gives you → you'll see your Todo app! 🎉

---

## PHASE 6 — See GitOps in Action

### Test 1 — Make a Code Change
Edit `app/app.py`, change the version badge from `v1.0` to `v2.0`

Then rebuild and push a new image:
```powershell
cd app
docker build -t YOUR_USERNAME/myapp:v2 .
docker push YOUR_USERNAME/myapp:v2
```

Update `k8s/deployment.yaml`:
```yaml
image: YOUR_USERNAME/myapp:v2
```

Commit and push:
```powershell
git add .
git commit -m "Update to v2"
git push
```

Watch Argo CD detect the change and auto-deploy within 3 minutes!

### Test 2 — Drift Detection (Self-Healing)
Manually delete a pod (simulating a mistake):
```powershell
kubectl delete pod -l app=myapp
```
Watch Argo CD self-heal and bring it back automatically.

### Test 3 — Rollback
In Argo CD UI:
- Click your app → History and Rollback
- Click on a previous version → Rollback
Done! No kubectl commands needed.

---

## QUICK REFERENCE COMMANDS

```powershell
# Start everything fresh
minikube start --driver=docker

# Port-forward Argo CD UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Check app status
kubectl get pods
kubectl get svc

# Access your app
minikube service myapp-service --url

# Check Argo CD apps
kubectl get applications -n argocd

# View app logs
kubectl logs -l app=myapp

# Stop Minikube (saves memory when not using)
minikube stop
```

---

## TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| Pods stuck in `Pending` | `kubectl describe pod POD_NAME` — usually low resources |
| Image pull error | Check Docker Hub username in deployment.yaml |
| Argo CD shows `OutOfSync` | Click Sync in UI or `kubectl apply -f k8s/argocd-app.yaml` |
| Can't reach localhost:8080 | Make sure port-forward command is still running |
| Minikube won't start | Restart Docker Desktop first |

---

## WHAT YOU'VE LEARNED ✅
- GitOps: Git is the source of truth
- Argo CD watches your repo and syncs Kubernetes automatically
- Drift detection: if someone manually changes k8s, Argo CD fixes it
- Rollback: one click in the UI
- This is the actual DevOps workflow used in industry!
