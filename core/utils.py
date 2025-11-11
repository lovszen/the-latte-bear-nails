from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
from django.core.mail import EmailMessage
from .models import Budget
import requests
from django.conf import settings
from PIL import Image as PILImage
from io import BytesIO as IO

def generate_budget_pdf(budget):
    """
    Generate a PDF budget for the given Budget instance
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  
    )


    try:
        logo_url = "https://cdn.imgchest.com/files/05065870b1ff.png"
        response = requests.get(logo_url)
        if response.status_code == 200:
            image_stream = IO(response.content)
            img = PILImage.open(image_stream)

            img_width, img_height = img.size
            aspect_ratio = img_height / float(img_width)

            max_width = 2 * inch
            calculated_height = max_width * aspect_ratio

            logo_img = Image(image_stream, width=max_width, height=calculated_height)
            logo_img.hAlign = 'CENTER'
            elements.append(logo_img)
            elements.append(Spacer(0.2 * inch, 0.2 * inch))
        else:
            pass
    except Exception:
        pass

    title = Paragraph(f"Presupuesto - {budget.title}", title_style)
    elements.append(title)

    customer_info = [
        ['Cliente:', budget.customer_name],
        ['Email:', budget.customer_email],
        ['Fecha:', budget.created_at.strftime('%d/%m/%Y')],
    ]

    customer_table = Table(customer_info, colWidths=[2*inch, 4*inch])
    customer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))

    elements.append(customer_table)
    elements.append(Spacer(1, 20))

    # Budget items
    data = [['Producto', 'Cantidad', 'Precio Unitario', 'Subtotal']]

    for item in budget.items.all():
        data.append([
            item.product.nombre,
            str(item.quantity),
            f"${item.price}",
            f"${item.subtotal}"
        ])

    data.append(['', '', 'TOTAL:', f"${budget.total_amount}"])

    table = Table(data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, -1), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    return buffer

def send_budget_email(budget, pdf_buffer):
    """
    Send the budget PDF via email with custom HTML template
    """
    from django.conf import settings
    from django.template.loader import render_to_string
    import logging

    logger = logging.getLogger(__name__)

    if not getattr(settings, 'EMAIL_HOST', None):
        logger.warning("Email settings not configured - skipping email sending")
        print("Email settings not configured - skipping email sending")
        return False

    try:
        html_content = render_to_string('emails/budget_email.html', {'budget': budget})
        text_content = render_to_string('emails/budget_email.txt', {'budget': budget})

        subject = f"Presupuesto - {budget.title}"

        from django.core.mail import EmailMultiAlternatives
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@thelattenails.com'),
            to=[budget.customer_email],
        )


        email.attach_alternative(html_content, "text/html")


        email.attach('presupuesto.pdf', pdf_buffer.getvalue(), 'application/pdf')


        email.send()
        return True
    except Exception as e:

        logger.error(f"Error sending budget email: {e}")
        print(f"Error sending email: {e}")
        return False
    
def enviar_a_telegram(texto):
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": texto, "parse_mode": "HTML"}
    response = requests.post(url, json=payload)
    return response


def enviar_imagen_a_telegram(image_url):
    """
    This function sends an image to Telegram by its URL.
    Note: Telegram API requires either a file_id, an HTTP URL, or a file upload.
    """
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    
    payload = {
        "chat_id": chat_id,
        "photo": image_url,
        "caption": "Imagen recibida desde el chat web"
    }
    
    response = requests.post(url, json=payload)
    return response


def enviar_imagen_file_a_telegram(file_path):
    """
    Send an image file directly to Telegram
    """
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    
    with open(file_path, 'rb') as image_file:
        files = {'photo': image_file}
        data = {'chat_id': chat_id, 'caption': 'Imagen recibida desde el chat web'}
        response = requests.post(url, files=files, data=data)
    
    return response