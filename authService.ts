import  type { User } from '../types';

// Mock credentials for local testing
const DEMO_USER = {
  email: 'admin@Alishba.com',
  password: 'Password123',
  name: 'Haroon'
};

export const verifyCredentials = (email: string, password: string): { success: boolean; user?: User; error?: string } => {
  if (!email || !password) {
    return { success: false, error: 'Email and password are required.' };
  }

  // Check email match
  if (email.toLowerCase() !== DEMO_USER.email.toLowerCase()) {
    return { success: false, error: 'Invalid email address.' };
  }

  // Check password match
  if (password !== DEMO_USER.password) {
    return { success: false, error: 'Incorrect password.' };
  }

  return {
    success: true,
    user: { email: DEMO_USER.email, name: DEMO_USER.name }
  };
};