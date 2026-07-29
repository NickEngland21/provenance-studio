# Zero-spend deployment plan

## Selected host

Render Free Web Service is the current preferred deployment target. It supports
Docker and Python web services, provides a public `onrender.com` URL, permits
secret environment variables, and has a current free service tier. The app is
stateless on Render; all durable media and manifests live in Backblaze B2.

The free service spins down after 15 minutes without inbound traffic and can
take about one minute to wake. This is acceptable for a hackathon demonstration
only if the submission and video clearly mention the cold start and judges are
given a direct health/app URL. A paid instance is not authorized.

Hugging Face Docker Spaces was rejected for this zero-spend run because current
official documentation says creating a Docker or Gradio compute Space requires
a paid account plan, even though the CPU Basic hardware itself has no hourly
charge.

## Deployment boundary

No deployment has occurred. Deployment requires:

1. A public repository under the intended `NickEngland21` account.
2. A user-created Render account and acceptance of Render's terms.
3. A user-created Backblaze B2 bucket and least-privilege application key.
4. A user-created NVIDIA developer API key on its no-card free serverless tier,
   or an explicitly selected GMI Cloud account with usable provider credit.
5. Secret values entered directly by the user in Render; they must never be sent
   through chat, committed, logged, or embedded in a manifest.
6. A strong judge access token entered as `DEMO_ACCESS_TOKEN`; generation is
   denied without it and additionally capped in-process.

`render.yaml` declares the free Docker service and prompts for secret values via
`sync: false`. `Dockerfile` runs as an unprivileged user, exposes the Render port,
and includes a local health check.
