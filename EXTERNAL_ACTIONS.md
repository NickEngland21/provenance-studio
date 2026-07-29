# Minimal external actions requiring user authority

These actions remain blocked until the user authorizes the exact step. Do not
paste secrets into chat.

1. Confirm GitHub is authenticated as `NickEngland21`, then authorize creation
   and publication of the prepared repository.
2. Create or sign in to Devpost, accept the competition terms, and confirm UK
   eligibility and any required tax/identity statements.
3. Create or sign in to Backblaze, create one private B2 bucket, and generate a
   least-privilege application key scoped to that bucket.
4. Create or sign in to NVIDIA Developer and create a free NIM API key after
   personally accepting its terms. GMI Cloud remains an optional fallback; do
   not add a paid funding source without separate spend authority.
5. Create or sign in to Render, accept its terms, and authorize a Free Blueprint
   deployment. Enter secrets directly in Render.
6. Authorize the final public video upload and Devpost submission after reviewing
   the exact public text, repository, app, and video.

The intended secret handoff is direct entry into the hosting provider's secret
fields. Required names are listed in `.env.example`; actual values must never be
committed or copied into project records.
