import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import { Link } from "react-router-dom";
import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";

const getOauthGoogleUrl = () => {
  const { VITE_GOOGLE_CLIENT_ID, VITE_GOOGLE_AUTHORIZED_REDIRECT_URI } =
    import.meta.env;
  const rootUrl = "https://accounts.google.com/o/oauth2/v2/auth";
  const options = {
    redirect_uri: VITE_GOOGLE_AUTHORIZED_REDIRECT_URI,
    client_id: VITE_GOOGLE_CLIENT_ID,
    access_type: "offline",
    response_type: "code",
    prompt: "consent",
    scope: [
      "https://www.googleapis.com/auth/userinfo.profile",
      "https://www.googleapis.com/auth/userinfo.email",
    ].join(" "),
  };
  const qs = new URLSearchParams(options);
  return `${rootUrl}?${qs.toString()}`;
};

function Home() {
  const isAuthenticated = Boolean(localStorage.getItem("access_token"));
  const [userData, setUserData] = useState(null);
  useEffect(() => {
    const accessToken = localStorage.getItem("access_token"); // Assuming the token is stored in localStorage
    console.log("Test");
    console.log(accessToken);
    if (!accessToken) return;

    fetch("http://localhost:8000/api/oauth/user-info", {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    })
      .then((response) => response.json())
      .then((data) => setUserData(data))
      .catch((error) => console.error("Error fetching user data:", error));
  }, []);
  const oauthURL = getOauthGoogleUrl();
  console.log(oauthURL);
  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    window.location.reload();
  };
  return (
    <>
      <div>
        <div>
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </div>
        <div>
          <img src={reactLogo} className="logo react" alt="React logo" />
        </div>
      </div>
      <h1>OAuth Google</h1>
      <div>
        {isAuthenticated ? (
          <div>
            <p>Xin chào, bạn {userData?.name} đã login thành công</p>
            <button onClick={logout}>Click để logout</button>
          </div>
        ) : (
          <Link to={oauthURL}>Login with Google</Link>
        )}
      </div>
    </>
  );
}

export default Home;
