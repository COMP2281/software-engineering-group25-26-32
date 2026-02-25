document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const response = await fetch('http://localhost:8000/login?username=' + encodeURIComponent(username) + '&password=' + encodeURIComponent(password), {
        method: 'GET',
        credentials: 'include'
    });
    if (response.ok) {
        window.location.href = 'admin.html';
    } else {
        alert("Login failed: Invalid username or password");
        document.getElementById('password').value = ''; 
        document.getElementById('username').value = ''; 
        document.getElementById('username').focus();
    }
});

window.onload = async function() {
    const res = await fetch('http://localhost:8000/token', {
        method: 'GET',
        credentials: 'include'
    });
    if (res.ok) {
        window.location.href = 'admin';
    }
};