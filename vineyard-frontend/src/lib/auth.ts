export async function checkToken(access: string) {
    const res = await fetch('http://localhost:8080/api/token/verify/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: access }),
    });

    if (res.ok) {
        return true;
    } else {
        return false;
    }
}
