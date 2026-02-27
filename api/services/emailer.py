import re
import resend
from pathlib import Path
from api.config import RESEND_API_KEY, FROM_EMAIL


async def send_paper_email(to_email: str, paper_title: str, zip_path: Path):
    """
    Send email with ZIP attachment via Resend API.
    """
    if not RESEND_API_KEY:
        raise EnvironmentError("RESEND_API_KEY is not set")

    resend.api_key = RESEND_API_KEY

    with open(zip_path, "rb") as f:
        zip_content = f.read()

    html_body = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f7f7f7;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f7f7f7;padding:40px 20px;">
    <tr><td align="center">
      <table width="520" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:8px;overflow:hidden;">

        <!-- Logo -->
        <tr><td style="background:#0a0a0a;padding:32px 40px;">
          <span style="font-family:'SF Mono','Fira Mono','Consolas',monospace;font-size:22px;font-weight:700;color:#ffffff;letter-spacing:-0.5px;">PaperFlow</span>
        </td></tr>

        <!-- Body -->
        <tr><td style="padding:36px 40px 20px;">
          <p style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;font-size:20px;font-weight:600;color:#111;margin:0 0 8px;">
            {paper_title}
          </p>
          <p style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;font-size:14px;color:#555;margin:0 0 28px;line-height:1.5;">
            Your Obsidian-ready Markdown is attached as a ZIP file.
          </p>

          <table cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
            <tr>
              <td style="padding:0 0 10px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;font-size:13px;color:#333;">
                <span style="display:inline-block;width:8px;height:8px;background:#10b981;border-radius:50%;margin-right:10px;vertical-align:middle;"></span>
                YAML frontmatter with metadata
              </td>
            </tr>
            <tr>
              <td style="padding:0 0 10px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;font-size:13px;color:#333;">
                <span style="display:inline-block;width:8px;height:8px;background:#10b981;border-radius:50%;margin-right:10px;vertical-align:middle;"></span>
                LaTeX equations preserved
              </td>
            </tr>
            <tr>
              <td style="padding:0 0 10px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;font-size:13px;color:#333;">
                <span style="display:inline-block;width:8px;height:8px;background:#10b981;border-radius:50%;margin-right:10px;vertical-align:middle;"></span>
                Clickable figure, table &amp; reference links
              </td>
            </tr>
            <tr>
              <td style="padding:0 0 0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;font-size:13px;color:#333;">
                <span style="display:inline-block;width:8px;height:8px;background:#10b981;border-radius:50%;margin-right:10px;vertical-align:middle;"></span>
                Images bundled in images/ folder
              </td>
            </tr>
          </table>

          <div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:6px;padding:16px 20px;margin-bottom:28px;">
            <p style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;font-size:13px;color:#555;margin:0;line-height:1.6;">
              Unzip the attachment, drop the folder into your Obsidian vault, and everything just works.
            </p>
          </div>
        </td></tr>

        <!-- Footer -->
        <tr><td style="padding:0 40px 32px;">
          <div style="border-top:1px solid #eee;padding-top:20px;">
            <p style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;font-size:12px;color:#999;margin:0;">
              Sent by <span style="color:#666;">PaperFlow</span> &middot; PDF to Obsidian pipeline
            </p>
          </div>
        </td></tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""

    safe_name = re.sub(r'[<>:"/\\|?*]', '', paper_title).strip()[:100]

    params = {
        "from": "PaperFlow <delivery@paperflowing.com>",
        "to": [to_email],
        "subject": f"Your paper is ready: {paper_title}",
        "html": html_body,
        "attachments": [
            {
                "filename": f"{safe_name}.zip",
                "content": list(zip_content)
            }
        ]
    }

    resend.Emails.send(params)
