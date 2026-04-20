const TOKEN = 'pdf-qa-token';
const USER = 'pdf-qa-user';

export const getToken = () => localStorage.getItem(TOKEN);
export const getUsername = () => localStorage.getItem(USER);
export const setAuth = (t: string, u: string) => {
  localStorage.setItem(TOKEN, t);
  localStorage.setItem(USER, u);
};
export const clearAuth = () => {
  localStorage.removeItem(TOKEN);
  localStorage.removeItem(USER);
};