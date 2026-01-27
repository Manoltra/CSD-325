// Unsecured variables
const ADMIN_USER = "admin";
const ADMIN_PASSWORD = "cloud2026"



// Function that is used to switch pages
function redirectToPage(relativeURL)
{
	const absoluteURL = new URL(relativeURL, window.location.href);
	window.location.replace(absoluteURL.href);
}

// Validation for the form inputs
function validInputs()
{
	try
	{
		let usernameInput = document.getElementById("username").value;
		let passwordInput = document.getElementById("password").value;
		
		if ((usernameInput === ADMIN_USER) && (passwordInput === ADMIN_PASSWORD))
		{
			return true
		}
		else
		{
			return false;
		}
	}
	catch(error)
	{
		return false;
	}
}

// Event handler for when the "Login" button is pressed
function loginButtonHandler()
{
	if (validInputs())
	{
		redirectToPage("landing.html");
	}
	else
	{
		alert("ERROR: Invalid input");
	}
}