import re
import html
import resend
from pathlib import Path
from api.config import RESEND_API_KEY, FROM_EMAIL, CONTACT_EMAIL, MAX_PAGES


def _resolve_from_header() -> str:
    if "<" in FROM_EMAIL and ">" in FROM_EMAIL:
        return FROM_EMAIL
    return f"PaperFlow <{FROM_EMAIL}>"


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
        "from": _resolve_from_header(),
        "reply_to": CONTACT_EMAIL,
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


async def send_page_limit_email(to_email: str, title: str, page_count: int):
    """
    Send email when PDF exceeds the page limit.
    """
    if not RESEND_API_KEY:
        raise EnvironmentError("RESEND_API_KEY is not set")

    resend.api_key = RESEND_API_KEY

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
        <tr><td style="padding:36px 40px 28px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;font-size:14px;color:#333;line-height:1.7;">
          <p style="margin:0 0 16px;">Hi,</p>
          <p style="margin:0 0 16px;">Your paper &ldquo;{title}&rdquo; has {page_count} pages, which exceeds this PaperFlow instance&rsquo;s configured limit of {MAX_PAGES} pages.</p>
          <p style="margin:0 0 16px;">PaperFlow is designed to work either self-hosted or through a managed deployment, depending on your document volume and compliance needs.</p>
          <p style="margin:0 0 8px;">For full documents and batch processing:</p>
          <p style="margin:0 0 4px;">&bull; Commercial API &mdash; from $0.05/page, handles LaTeX, multi-column, footnotes</p>
          <p style="margin:0 0 4px;">&bull; MCP Server &mdash; use PaperFlow directly inside Claude Desktop</p>
          <p style="margin:0 0 16px;">&bull; Private deployment &mdash; self-hosted for enterprise environments</p>
          <p style="margin:0 0 28px;">Contact us: <a href="mailto:{CONTACT_EMAIL}" style="color:#333;">{CONTACT_EMAIL}</a></p>
          <p style="margin:0;">&mdash; PaperFlow</p>
        </td></tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""

    params = {
        "from": _resolve_from_header(),
        "reply_to": CONTACT_EMAIL,
        "to": [to_email],
        "subject": "PaperFlow: Your PDF exceeds the free limit",
        "html": html_body,
    }

    resend.Emails.send(params)


async def send_failure_email(to_email: str, original_filename: str):
    """
    Send email when processing fails unexpectedly.
    """
    if not RESEND_API_KEY:
        raise EnvironmentError("RESEND_API_KEY is not set")

    resend.api_key = RESEND_API_KEY
    safe_name = html.escape(original_filename or "your PDF")

    html_body = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f7f7f7;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f7f7f7;padding:40px 20px;">
    <tr><td align="center">
      <table width="520" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:8px;overflow:hidden;">
        <tr><td style="background:#0a0a0a;padding:32px 40px;">
          <span style="font-family:'SF Mono','Fira Mono','Consolas',monospace;font-size:22px;font-weight:700;color:#ffffff;letter-spacing:-0.5px;">PaperFlow</span>
        </td></tr>
        <tr><td style="padding:36px 40px 24px;">
          <p style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;font-size:16px;font-weight:600;color:#111;margin:0 0 16px;">
            We couldn't finish processing your PDF
          </p>
          <p style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;font-size:14px;color:#555;margin:0 0 12px;line-height:1.6;">
            File: <strong>{safe_name}</strong>
          </p>
          <p style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;font-size:14px;color:#555;margin:0;line-height:1.6;">
            Please try again. If it fails again, send the PDF to
            <a href="mailto:{CONTACT_EMAIL}" style="color:#7c8aff;">{CONTACT_EMAIL}</a>
            and we'll investigate.
          </p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""

    params = {
        "from": _resolve_from_header(),
        "reply_to": CONTACT_EMAIL,
        "to": [to_email],
        "subject": "PaperFlow: Processing failed",
        "html": html_body,
    }

    resend.Emails.send(params)
