import { writable } from 'svelte/store';

interface AuthState {
    access: string | null;
    refresh: string | null;
}

const stored =
    typeof localStorage !== 'undefined'
        ? JSON.parse(
              localStorage.getItem('auth') || '{"access":null,"refresh":null}'
          )
        : { access: null, refresh: null };

export const auth = writable<AuthState>(stored);

auth.subscribe((value) => {
    if (typeof localStorage !== 'undefined') {
        localStorage.setItem('auth', JSON.stringify(value));
    }
});
