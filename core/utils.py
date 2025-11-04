from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
from django.core.mail import EmailMessage
from .models import Budget

def generate_budget_pdf(budget):
    """
    Generate a PDF budget for the given Budget instance
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    # Title
    title = Paragraph(f"Presupuesto - {budget.title}", title_style)
    elements.append(title)
    
    # Customer info
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
    
    # Add total
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
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer

def send_budget_email(budget, pdf_buffer):
    """
    Send the budget PDF via email
    """
    from django.conf import settings
    import logging

    logger = logging.getLogger(__name__)
    
    subject = f"Presupuesto - {budget.title}"
    message = f"Estimado {budget.customer_name},\n\nAdjunto encontrará el presupuesto solicitado.\n\nSaludos,\nEquipo de The Latte Bear Nails"
    
    try:
        email = EmailMessage(
            subject,
            message,
            getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@thelattebear.com'),  # From email from settings
            [budget.customer_email],  # To email
        )
        
        # Attach the PDF
        email.attach('presupuesto.pdf', pdf_buffer.getvalue(), 'application/pdf')
        
        # Send the email
        email.send()
        return True
    except Exception as e:
        # Log the error
        logger.error(f"Error sending budget email: {e}")
        print(f"Error sending email: {e}")  # For development
        # In development, we can write the email to console/file instead
        return False