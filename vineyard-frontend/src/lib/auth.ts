import { goto } from '$app/navigation';

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

export async function gotoIfStudent(accessToken: string, path: string) {
    const resUser = await fetch('http://localhost:8080/api/me/', {
        headers: { Authorization: `Bearer ${accessToken}` },
    });
    if (resUser.ok) {
        const data = await resUser.json();
        if (data.role == 'student') {
            goto(path);
        }
    }
}
