export const otpEmailTemplate = (otp) => {

    
    return `
  <div style="font-family: Arial, sans-serif; max-width: 480px; margin: auto; padding: 24px; border: 1px solid #e0e0e0; border-radius: 8px;">
    <h2 style="color: #1a1a1a;">Password Reset Request</h2>
    <p style="color: #444; font-size: 15px;">
      We received a request to reset your password for your SDIP account.
      Use the OTP below to proceed. This code is valid for 5 minutes.
    </p>
    <div style="background: #f5f5f5; padding: 16px; text-align: center; border-radius: 6px; margin: 20px 0;">
      <span style="font-size: 28px; letter-spacing: 6px; font-weight: bold; color: #1a1a1a;">${otp}</span>
    </div>
    <p style="color: #777; font-size: 13px;">
      If you did not request this, please ignore this email. Your password will remain unchanged.
    </p>
    <p style="color: #aaa; font-size: 12px; margin-top: 24px;">— SDIP Team</p>
  </div>
`;
}