// Function that is used to switch pages
function redirectToPage(relativeURL)
{
	const absoluteURL = new URL(relativeURL, window.location.href);
	window.location.replace(absoluteURL.href);
}

// handles login button click and sends credentials to flask
async function loginButtonHandler() {

	let usernameInput = document.getElementById("username").value;
	let passwordInput = document.getElementById("password").value;

	try {
		const res = await fetch("/login", {
			method: "POST",
			headers: {
				"Content-Type": "application/json"
			},
			body: JSON.stringify({
				username: usernameInput,
				password: passwordInput
			})
		});

		const result = await res.json();

		if (res.success) {
			redirectToPage("landing.html");
		} else {
			alert("ERROR: Invalid input");
		}
	
} catch (error) {
	alert("ERROR: Server not responding");
}

}
