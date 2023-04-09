export type ServerUser = {
  id: number;
  username: string;
  nickname: string;
  student_code: string;
};

export async function getUsers() {
  const url = new URL(window.location.toString());
  const headId = Number(url.searchParams.get("id"));
  const res = await fetch(`${import.meta.env.VITE_BASE_URL}/teams/${headId}`, {
    method: "GET",
  });

  if (!res.ok) {
    throw new Error(res.statusText);
  }

  return JSON.parse(await res.text()) as ServerUser[];
}
