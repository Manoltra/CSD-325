// Function that is used to switch pages
function redirectToPage(relativeURL)
{
	const absoluteURL = new URL(relativeURL, window.location.href);
	window.location.replace(absoluteURL.href);
}


// Event handler for when the "Login" button is pressed
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
		redirectToPage(result.redirect);
	}
	else
	{
		alert(result.message || "Invalid input");
	}
}

async function registerButtonHandler() {
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    try {
        const response = await fetch('https://mr53kfv9dg.execute-api.us-west-2.amazonaws.com/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({email, password })
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('Registration successful! Please log in.');
            // window.location.href = '/login';
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
       alert('Login Sucsessful! To complete login, please Authenticate account');
	}
	else
	{
		alert(result.message);
	}
}

async function veryfyMFAHandler() {
    
    const username = sessionStorage.getItem("username");
    const codeInput = document.getElementById('password').value;
    const response = await fetch("https://mr53kfv9dg.execute-api.us-west-2.amazonaws.com/verify-mfa", 
	{
        method: "POST",
        headers: 
		{
            "Content-Type": "application/json"
        },
        body: JSON.stringify({username, codeInput})
    });
    const result = await response.json();

    if (response.ok && result.success)
	{   
       alert('Sucsess! Redirecting...');
       redirectToPage(result.redirect);
	}
	else
	{
		alert(result.message);
	}


}