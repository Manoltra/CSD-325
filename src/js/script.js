function redirectToPage(relativeURL)
{
	const absoluteURL = new URL(relativeURL, window.location.href);
	window.location.replace(absoluteURL.href);
}

async function loginButtonHandler()
{
	const username = document.getElementById("username").value;
	const password = document.getElementById("password").value;
	const response = await fetch("https://mr53kfv9dg.execute-api.us-west-2.amazonaws.com/login", 
	{
        method: "POST",
        headers: 
		{
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, password })
    });
    const result = await response.json();
	if (response.ok && result.success)
	{
        sessionStorage.setItem("username", username);
		redirectToPage("mfa.html");
	}
	else
	{
		alert(result.message || "Invalid input");
	}
}

async function registerButtonHandler() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    try {
        const response = await fetch('https://mr53kfv9dg.execute-api.us-west-2.amazonaws.com/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({username, password })
        });
        const result = await response.json();
        if (result.success) {
            alert('Registration successful! Please log in.');
			redirectToPage('login.html');
        } else {
            alert('Registration failed: ' + result.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Server error. Please try again.');
    }
}

async function mfa_initHandler()
{
    const username = sessionStorage.getItem("username");
    const response = await fetch("https://mr53kfv9dg.execute-api.us-west-2.amazonaws.com/send-mfa", 
	{
        method: "POST",
        headers: 
		{
            "Content-Type": "application/json"
        },
        body: JSON.stringify({username})
    });
    const result = await response.json();
    if (response.ok && result.success)
	{   
       alert('Code sent. Check your email.');
	}
	else
	{
		alert(result.message);
	}
}

async function verifyMFAHandler() {
    const username = sessionStorage.getItem("username");
    const code = document.getElementById('mfa-code').value;
    const action = sessionStorage.getItem("mfa_action") || "login";
    const response = await fetch("https://mr53kfv9dg.execute-api.us-west-2.amazonaws.com/verify-mfa", 
	{
        method: "POST",
        headers: 
		{
            "Content-Type": "application/json"
        },
        body: JSON.stringify({username, code, action})
    });
    const result = await response.json();
    if (response.ok && result.success) {
        if (action == "update") {
            await submitUpdateHandler();
        } else {
            alert('Success! Redirecting...');
            redirectToPage(result.redirect);
        }
    }
	else
	{
		alert(result.message);
	}
}

// stores profile updated data and triggers MFA
async function updateProfileHandler() {

    const old_username = sessionStorage.getItem("username");  // fixed
    const old_password = document.getElementById('old-password').value;
    const new_password = document.getElementById('new-password').value;

    sessionStorage.setItem("update_old_username", old_username);
    sessionStorage.setItem("update_old_password", old_password);
    sessionStorage.setItem("update_new_password", new_password);

    const response = await fetch("https://mr53kfv9dg.execute-api.us-west-2.amazonaws.com/login", {
        method: "POST",
        headers:
        {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({username: old_username, password: old_password})
    });
    const result = await response.json();
    if (response.ok && result.success) {
        sessionStorage.setItem("mfa_action", "update");
        sessionStorage.setItem("username", old_username);
        redirectToPage("mfa.html");
    } else {
        alert(result.message || "Failed to send code.");
    }
}

// called after MFA verification, submits the update    
async function submitUpdateHandler() {

    const old_username = sessionStorage.getItem("update_old_username");
    const old_password = sessionStorage.getItem("update_old_password");
    const new_password = sessionStorage.getItem("update_new_password");

    const response = await fetch("https://mr53kfv9dg.execute-api.us-west-2.amazonaws.com/update-username",
    {
        method: "POST",
        headers:   
        {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({old_username, old_password, new_username: old_username, new_password})
    });
    const result = await response.json(); 
    if (response.ok && result.success) {
        sessionStorage.clear();
        alert("Profile updated successfully!")
        redirectToPage("landing.html");
    } else {
        alert(result.message || "Update failed.");
    }
}