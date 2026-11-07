export interface WebUser {
  id: string;
}

export async function getUser(_request: Request): Promise<WebUser | null> {
  // TODO: Replace this with your app's authentication.
  return { id: "local-user" };
}
