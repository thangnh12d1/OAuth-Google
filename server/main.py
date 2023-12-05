from fastapi import FastAPI, HTTPException, Request
import httpx
from fastapi.responses import RedirectResponse
from jose import jwt

app = FastAPI()
port = 8000
GOOGLE_CLIENT_ID="584725740860-49vboebtd48lk8sumo2lipjp9kkt375h.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="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"
GOOGLE_AUTHORIZED_REDIRECT_URI="http://localhost:8000/api/oauth/google"
AC_PRIVATE_KEY="access_token_private_key"
RF_PRIVATE_KEY="refresh_token_private_key"

async def get_oauth_google_token(code: str):
    body = {
        'code': code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': GOOGLE_AUTHORIZED_REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://oauth2.googleapis.com/token', json=body)
    return response.json()

async def get_google_user(id_token: str, access_token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            'https://www.googleapis.com/oauth2/v1/userinfo',
            params={'access_token': access_token, 'alt': 'json'},
            headers={'Authorization': f'Bearer {id_token}'}
        )
    return response.json()

@app.get('/api/oauth/google')
async def oauth_google(request: Request):
    code = request.query_params.get('code')
    if not code:
        raise HTTPException(status_code=400, detail="Missing code parameter")

    data = await get_oauth_google_token(code)
    id_token = data.get('id_token')
    access_token = data.get('access_token')
    google_user = await get_google_user(id_token, access_token)

    if not google_user.get('verified_email'):
        raise HTTPException(status_code=403, detail="Google email not verified")

    manual_access_token = jwt.encode(
        {'email': google_user['email'], 'type': 'access_token'},
        AC_PRIVATE_KEY,
        algorithm='HS256'
    )
    manual_refresh_token = jwt.encode(
        {'email': google_user['email'], 'type': 'refresh_token'},
        RF_PRIVATE_KEY,
        algorithm='HS256'
    )
    # Construct the URL to which you want to redirect
    redirect_url = f"http://localhost:3000/login/oauth?access_token={manual_access_token}&refresh_token={manual_refresh_token}"


    return RedirectResponse(url=redirect_url)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
