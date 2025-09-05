from fpdf import FPDF
from PIL import Image
import os
import qrcode
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
from reportlab.lib.utils import ImageReader
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.lib import colors
from datetime import datetime, timedelta
from reportlab.graphics.shapes import Path
from reportlab.pdfbase.pdfmetrics import stringWidth
import re
from PyPDF2 import PdfMerger
import file_utils
import constants
#from file_utils import get_image_reader

def draw_id_card_front(c, x_offset, y_offset, width, height, name, designation, dob, phone, blood_group, email, photo_path, address, member_id=None, rnrm_number=None, issue_date=None, nurse_signature_path=None, auth_signature_path=None):

    # Draw a white rounded rectangle as the card background for curved edges
    corner_radius = 5*mm
    card_x = x_offset
    card_y = y_offset
    card_w = width
    card_h = height
    c.setFillColor(colors.white)
    c.roundRect(card_x, card_y, card_w, card_h, corner_radius, fill=1, stroke=0)
    # Draw solid color behind the logo area
    logo_w = 10*mm
    logo_x = x_offset + 1*mm
    bar_height = 14*mm
    left_color = colors.Color(25/255, 118/255, 210/255)  # #1976d2
    c.setFillColor(left_color)
    c.rect(x_offset, y_offset + height - bar_height, logo_x + logo_w - x_offset, bar_height, fill=1, stroke=0)
    # Draw gradient for the rest of the bar
    n_steps = int(width)
    left_rgb = (25, 118, 210)
    right_rgb = (67, 206, 162)
    for i in range(n_steps):
        frac = i / (n_steps - 1)
        r = int(left_rgb[0] + (right_rgb[0] - left_rgb[0]) * frac)
        g = int(left_rgb[1] + (right_rgb[1] - left_rgb[1]) * frac)
        b = int(left_rgb[2] + (right_rgb[2] - left_rgb[2]) * frac)
        x = logo_x + logo_w - x_offset + i * ((width - (logo_x + logo_w - x_offset)) / n_steps)
        c.setFillColor(colors.Color(r/255, g/255, b/255))
        c.rect(x_offset + x, y_offset + height - bar_height, (width - (logo_x + logo_w - x_offset)) / n_steps + 1, bar_height, fill=1, stroke=0)
    # Draw logo at far left of bar
    logo_path = constants.logo_path
    logo_h = 10*mm
    logo_y = y_offset + height-bar_height+2*mm

    logo_reader = file_utils.get_image_reader(logo_path)

    if logo_reader:
        c.drawImage(logo_reader, logo_x, logo_y, logo_w, logo_h, mask='auto')
    else:
        print("Logo path is None or invalid:", logo_path)

    # Draw association name next to logo, vertically centered
    assoc_font_size = 6.5
    assoc_text = 'MRB COVID NURSES ASSOCIATION'
    c.setFont('Helvetica-Bold', assoc_font_size)
    c.setFillColor(colors.white)
    text_x = logo_x + logo_w + 1*mm
    text_y = logo_y + logo_h/2 - assoc_font_size/2.5
    c.drawString(text_x, text_y, assoc_text)
    # Add '58/2022' below the association name, centered
    c.setFont('Helvetica', 6)
    c.setFillColor(colors.white)
    c.drawCentredString(x_offset + width/2, text_y - 4*mm, 'REG.NO. 58/2022')
    # Draw hospital symbol icon (right side of top bar, below association name)
    hospital_symbol_path = 'hospital_symbol.png'  # Path to your icon
    icon_w = 8*mm
    icon_h = 5*mm
    icon_x = x_offset + width - icon_w - 2*mm  # 4mm from right edge for more space
    icon_y = text_y - 6*mm  # Significantly lowered position

    hospital_symbol_reader = file_utils.get_image_reader(hospital_symbol_path)
    if hospital_symbol_reader:
        c.drawImage(hospital_symbol_reader, icon_x, icon_y, icon_w, icon_h, mask='auto')

    # Draw photo (centered, below bar)
    photo_y = y_offset + height - bar_height - 19*mm
    photo_reader = file_utils.get_image_reader(photo_path)
    if photo_reader:
        c.setFillColor(colors.white)
        c.circle(x_offset + width/2, photo_y+9*mm, 9*mm, fill=1, stroke=0)
        c.drawImage(photo_reader, x_offset + width/2-8*mm, photo_y, 16*mm, 18*mm, mask='auto')

    # Name (bold, black, centered) - place below the photo
    name_y_below_photo = photo_y - 4*mm  # Adjust spacing as needed
    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(colors.black)
    c.drawCentredString(x_offset + width/2, name_y_below_photo, name)
    # Designation (smaller, secondary color, centered)
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.HexColor('#1976d2'))
    c.drawCentredString(x_offset + width/2, name_y_below_photo - 4*mm, designation)
    # Details table section
    if issue_date:
        try:
            issue_dt = datetime.strptime(issue_date, '%Y-%m-%d')
        except Exception:
            issue_dt = datetime.today()
    else:
        issue_dt = datetime.today()
    valid_till = issue_dt + timedelta(days=365)
    issue_date_str = issue_dt.strftime('%d-%m-%Y')
    valid_till_str = valid_till.strftime('%d-%m-%Y')
    try:
        dob_dt = datetime.strptime(dob, '%Y-%m-%d')
        dob_str = dob_dt.strftime('%d-%m-%Y')
    except Exception:
        dob_str = str(dob) if dob else '-'
    field_x = x_offset + 4*mm
    colon_x = x_offset + 26*mm
    value_x = x_offset + 28*mm
    row_height = 5*mm
    details_y = photo_y - 14*mm
    fields = [
        ("RNRM Number", str(rnrm_number) if rnrm_number else '-'),
        ("DOB", dob_str),
        ("Blood Group", str(blood_group) if blood_group else '-'),
        ("Issue Date", issue_date_str),
        ("Valid Till", valid_till_str),
    ]
    for i, (field, value) in enumerate(fields):
        y = details_y - i*row_height
        c.setFont('Helvetica', 7)
        c.setFillColor(colors.black)
        c.drawString(field_x, y, field)
        c.drawString(colon_x, y, ":")
        c.drawString(value_x, y, value)
    # Signature section
    sig_y = details_y - len(fields)*row_height - 4*mm  # Move up by 2mm
    sig_img_h = 7*mm
    sig_img_w = 18*mm
    right_margin = 2*mm
    auth_x = x_offset + width - right_margin - sig_img_w

    sign_reader = file_utils.get_image_reader(auth_signature_path)
    if sign_reader:
        c.drawImage(sign_reader, auth_x, sig_y, sig_img_w, sig_img_h, mask='auto')

    c.setFont('Helvetica', 7)
    c.setFillColor(colors.black)
    c.drawRightString(x_offset + width - right_margin, sig_y - 2*mm, "Authorized Signatory")
    # Footer (stylish curved bottom bar - wave)
    bottom_bar_height = 4*mm
    bottom_bar_curve = 4*mm
    p = c.beginPath()
    p.moveTo(x_offset, y_offset + bottom_bar_height)
    p.curveTo(
        x_offset + width*0.25, y_offset + bottom_bar_height + bottom_bar_curve,
        x_offset + width*0.75, y_offset + bottom_bar_height - bottom_bar_curve,
        x_offset + width, y_offset + bottom_bar_height
    )
    p.lineTo(x_offset + width, y_offset)
    p.lineTo(x_offset, y_offset)
    p.close()
    c.setFillColor(colors.Color(25/255, 118/255, 210/255))  # Blue color
    c.drawPath(p, fill=1, stroke=0)

def draw_id_card_back(c, x_offset, y_offset, width, height, name, designation, dob, phone, blood_group, email, photo_path, address, member_id=None, rnrm_number=None, issue_date=None, nurse_signature_path=None, auth_signature_path=None, assoc_addr=None, assoc_contact=None, assoc_email=None, emergency_contact=None):
    # (Move the back side drawing logic here, replacing all x/y with x_offset/y_offset as needed)
    # Draw a white rounded rectangle as the card background for curved edges
    corner_radius = 5*mm
    card_x = x_offset
    card_y = y_offset
    card_w = width
    card_h = height
    c.setFillColor(colors.white)
    c.roundRect(card_x, card_y, card_w, card_h, corner_radius, fill=1, stroke=0)
    # Draw solid blue rectangle for top bar (no white at top)
    top_bar_height = 2*mm
    c.setFillColor(colors.Color(25/255, 118/255, 210/255))
    c.rect(x_offset, y_offset + height - top_bar_height, width, top_bar_height, fill=1, stroke=0)
    # Draw wave at the bottom edge of the top bar
    wave_height = 6*mm
    wave_curve = 0*mm
    p_top = c.beginPath()
    p_top.moveTo(x_offset, y_offset + height - top_bar_height)
    p_top.curveTo(x_offset + width*0.25, y_offset + height - top_bar_height + wave_curve, x_offset + width*0.75, y_offset + height - top_bar_height - wave_curve, x_offset + width, y_offset + height - top_bar_height)
    p_top.lineTo(x_offset + width, y_offset + height - top_bar_height + wave_height)
    p_top.lineTo(x_offset, y_offset + height - top_bar_height + wave_height)
    p_top.close()
    c.setFillColor(colors.Color(25/255, 118/255, 210/255))
    c.drawPath(p_top, fill=1, stroke=0)
    # Draw curved (wave) bottom bar, increase height to fit association info
    bottom_bar_height = 25*mm
    bottom_bar_curve = 4*mm
    p_bot = c.beginPath()
    p_bot.moveTo(x_offset, y_offset + bottom_bar_height)
    p_bot.curveTo(x_offset + width*0.25, y_offset + bottom_bar_height+bottom_bar_curve, x_offset + width*0.75, y_offset + bottom_bar_height-bottom_bar_curve, x_offset + width, y_offset + bottom_bar_height)
    p_bot.lineTo(x_offset + width, y_offset)
    p_bot.lineTo(x_offset, y_offset)
    p_bot.close()
    c.setFillColor(colors.Color(0/255, 153/255, 122/255))  # Darker green for better contrast
    c.drawPath(p_bot, fill=1, stroke=0)
    # Set y position for content
    content_y = y_offset + height - top_bar_height - 8*mm
    icon_size = 4*mm
    text_x = x_offset + 14*mm
    icon_x = x_offset + 2*mm
    row_gap = 5*mm
    line_height = 3.5*mm
    font_height = 2.8*mm  # Approximate for 8pt font
    font_size = 8  # For icon alignment
    # Tabular layout for Address, Phone, Email
    labels = ["Address", "Phone", "Email"]
    label_widths = [stringWidth(label, 'Helvetica-Bold', font_size) for label in labels]
    max_label_width = max(label_widths)
    colon_gap = 1.5*mm
    value_gap = 1*mm  # Gap after colon
    value_x = icon_x + max_label_width + colon_gap + value_gap
    line_y = content_y
    c.setFillColor(colors.black)
    max_width = width - (value_x - x_offset) - 4*mm  # Ensure max_width is assigned before use
    # Address
    address_label = "Address"
    c.setFont('Helvetica-Bold', font_size)
    c.drawString(icon_x, line_y, address_label)
    c.drawString(icon_x + max_label_width, line_y, ":")
    c.setFont('Helvetica', font_size)
    segments = [seg.strip() for seg in address.split(',')]
    addr_lines = []
    line = ""
    for seg in segments:
        test_line = (line + ", " + seg) if line else seg
        if stringWidth(test_line, 'Helvetica', font_size) <= max_width:
            line = test_line
        else:
            if line:
                addr_lines.append(line)
            line = seg  # Start new line with this segment
    if line:
        addr_lines.append(line)
    for i, l in enumerate(addr_lines):
        if i == 0:
            c.drawString(value_x, line_y, l)
        else:
            line_y -= line_height
            c.drawString(value_x, line_y, l)
    # After all address lines, apply row_gap
    line_y -= row_gap
    # Phone
    phone_label = "Phone"
    c.setFont('Helvetica-Bold', font_size)
    c.drawString(icon_x, line_y, phone_label)
    c.drawString(icon_x + max_label_width, line_y, ":")
    c.setFont('Helvetica', font_size)
    phone_value = phone
    c.drawString(value_x, line_y, phone_value)
    # After phone, apply row_gap
    line_y -= row_gap
    # ICE (Emergency Contact)
    if emergency_contact:
        ice_label = "ICE"
        c.setFont('Helvetica-Bold', font_size)
        c.drawString(icon_x, line_y, ice_label)
        c.drawString(icon_x + max_label_width, line_y, ":")
        c.setFont('Helvetica', font_size)
        c.drawString(value_x, line_y, emergency_contact)
        line_y -= row_gap
    # Email (with wrapping)
    email_label = "Email"
    c.setFont('Helvetica-Bold', font_size)
    c.drawString(icon_x, line_y, email_label)
    c.drawString(icon_x + max_label_width, line_y, ":")
    c.setFont('Helvetica', font_size)
    email_lines = []
    line = ""
    for word in email.split():
        test_line = (line + " " + word) if line else word
        if stringWidth(test_line, 'Helvetica', font_size) < max_width:
            line = test_line
        else:
            if line:
                email_lines.append(line)
            line = word
    if line:
        email_lines.append(line)

    for i, l in enumerate(email_lines):
        if i == 0:
            c.drawString(value_x, line_y, l)
        else:
            line_y -= line_height
            c.drawString(value_x, line_y, l)
    # Association name and address in bottom bar, centered and wrapped
    assoc_text = "MRB COVID NURSES ASSOCIATION"
    # Use provided association address, contact, and email
    assoc_addr = assoc_addr or "-"
    assoc_contact = assoc_contact or "-"
    assoc_email = assoc_email or "-"
    c.setFont('Helvetica-Bold', 8)
    c.setFillColor(colors.white)
    c.drawCentredString(x_offset + width/2, y_offset + bottom_bar_height - 7*mm, assoc_text)
    # Wrap and draw association address, contact, and email
    c.setFont('Helvetica', 7)
    max_width = width - 8*mm
    y = y_offset + bottom_bar_height - 11*mm
    # Wrap address
    addr_lines = []
    line = ""
    for word in assoc_addr.split():
        test_line = line + (" " if line else "") + word
        if stringWidth(test_line, 'Helvetica', 7) < max_width:
            line = test_line
        else:
            addr_lines.append(line)
            line = word
    if line:
        addr_lines.append(line)
    for l in addr_lines:
        c.drawCentredString(x_offset + width/2, y, l)
        y -= 3.5*mm
    # Contact
    c.drawCentredString(x_offset + width/2, y, assoc_contact)
    y -= 3.5*mm
    # Email
    c.drawCentredString(x_offset + width/2, y, assoc_email)

def generate_id_card_pdf_side_by_side(
    output_path, name, designation, dob, phone, blood_group, email, photo_path, address,
    member_id=None, rnrm_number=None, issue_date=None, nurse_signature_path=None, auth_signature_path=None,
    assoc_addr=None, primary_contact=None, secondary_contact=None, assoc_email=None, emergency_contact=None
):
    card_width, card_height = 54*mm, 86*mm
    gap = 8*mm  # 8mm gap between front and back
    c = canvas.Canvas(output_path, pagesize=(2*card_width + gap, card_height))
    # Draw front side on the left
    draw_id_card_front(
        c, 0, 0, card_width, card_height,
        name=name,
        designation=designation,
        dob=dob,
        phone=phone,
        blood_group=blood_group,
        email=email,
        photo_path=photo_path,
        address=address,
        member_id=member_id,
        rnrm_number=rnrm_number,
        issue_date=issue_date,
        nurse_signature_path=nurse_signature_path,
        auth_signature_path=auth_signature_path
    )
    # Prepare contact string
    if primary_contact and secondary_contact:
        assoc_contact = f"{primary_contact} / {secondary_contact}"
    else:
        assoc_contact = primary_contact or secondary_contact or "-"
    # Draw back side on the right, after the gap
    draw_id_card_back(
        c=c,
        x_offset=card_width + gap,
        y_offset=0,
        width=card_width,
        height=card_height,
        name=name,
        designation=designation,
        dob=dob,
        phone=phone,
        blood_group=blood_group,
        email=email,
        photo_path=photo_path,
        address=address,
        member_id=member_id,
        rnrm_number=rnrm_number,
        issue_date=issue_date,
        nurse_signature_path=nurse_signature_path,
        auth_signature_path=auth_signature_path,
        assoc_addr=assoc_addr,
        assoc_contact=assoc_contact,
        assoc_email=assoc_email,
        emergency_contact=emergency_contact
    )
    c.save()

def generate_profile_pdf_with_disclaimers(
    output_path,
    name,
    designation,
    dob,
    phone,
    email,
    address,
    member_id,
    aadhaar,
    workplace,
    college,
    educational_qualification,
    blood_group,
    gender,
    emergency_contact,
    rnrm_number,
    disclaimer1_text,
    disclaimer2_text,
    signature_path=None,
    association_name=None,
    association_reg=None,
    association_email=None,
    primary_contact=None,
    secondary_contact=None,
    profile_photo_path=None,
    auth_signature_path=None
):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    from reportlab.lib.utils import ImageReader
    from reportlab.lib import colors
    import os
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    y = height - 40
    left = 40
    right = width - 40
    center = width / 2
    label_style = ('Helvetica-Bold', 11)
    value_style = ('Helvetica', 11)
    line_gap = 22
    # --- Association Info Header ---
    c.setFont('Helvetica-Bold', 15)
    c.setFillColor(colors.HexColor('#1a237e'))
    c.drawCentredString(center, y, association_name or "Association Name")
    y -= 22
    c.setFont('Helvetica', 11)
    c.setFillColor(colors.HexColor('#333'))
    c.drawCentredString(center, y, f"Reg. No: {association_reg or '-'}")
    y -= 18
    c.drawCentredString(center, y, f"Email: {association_email or '-'}")
    y -= 18
    contact_str = f"Contact: {primary_contact or '-'}"
    if secondary_contact:
        contact_str += f" / {secondary_contact}"
    c.drawCentredString(center, y, contact_str)
    y -= 18
    # --- Line Separator ---
    c.setStrokeColor(colors.HexColor('#1976d2'))
    c.setLineWidth(1.2)
    c.line(left, y, right, y)
    y -= 28
    # --- Membership Form Heading ---
    c.setFont('Helvetica-Bold', 14)
    c.setFillColor(colors.HexColor('#1976d2'))
    c.drawCentredString(center, y, "Membership Form")
    y -= 30
    # --- Profile Details Table with Photo on Right ---
    table_left = left
    table_top = y
    table_colon_x = left + 170
    table_value_x = left + 190
    table_width = 320
    photo_size = 90
    photo_x = table_left + table_width + 20
    photo_y = table_top - 10
    fields = [
        ("Member ID", member_id),
        ("Name", name),
        ("Designation", designation),
        ("Date of Birth", dob),
        ("Gender", gender),
        ("Mail ID", email),
        ("Phone Number", phone),
        ("Emergency Contact", emergency_contact),
        ("Aadhaar Number", aadhaar),
        ("Hospital Name", workplace),
        ("RNRM Number", rnrm_number),
        ("Studied College", college),
        ("Educational Qualification", educational_qualification),
        ("Blood Group", blood_group),
        ("Address", address),
    ]
    c.setFont('Helvetica-Bold', 11)
    c.setFillColor(colors.HexColor('#333'))
    y_table = table_top
    for label, value in fields:
        if label == "Address":
            # Split address by commas and clean up
            address_segments = [seg.strip() for seg in str(value).split(',') if seg.strip()]
            # Calculate max width from value_x to right margin
            max_addr_width = right - table_value_x - 10  # 10pt padding from right
            lines = []
            current_line = ""
            
            # First line with label
            c.drawString(table_left, y_table, label)
            c.drawString(table_colon_x, y_table, ":")
            c.setFont('Helvetica', 11)
            c.setFillColor(colors.HexColor('#111'))
            
            # Process address segments
            for seg in address_segments:
                test_line = (current_line + ", " + seg) if current_line else seg
                if stringWidth(test_line, 'Helvetica', 11) <= max_addr_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = seg
            
            # Add the last line if there is one
            if current_line:
                lines.append(current_line)
            
            # Draw the first line
            if lines:
                c.drawString(table_value_x, y_table, lines[0])
                y_table -= line_gap
                
                # Draw remaining lines with proper indentation
                for line in lines[1:]:
                    c.drawString(table_value_x, y_table, line)
                    y_table -= line_gap
            
            # Reset font for next field
            c.setFont('Helvetica-Bold', 11)
            c.setFillColor(colors.HexColor('#333'))
        else:
            c.drawString(table_left, y_table, label)
            c.drawString(table_colon_x, y_table, ":")
            c.setFont('Helvetica', 11)
            c.setFillColor(colors.HexColor('#111'))
            c.drawString(table_value_x, y_table, str(value) if value else '-')
            c.setFont('Helvetica-Bold', 11)
            c.setFillColor(colors.HexColor('#333'))
            y_table -= line_gap

    # --- Profile Photo (right of table) ---
    photo_reader = file_utils.get_image_reader(profile_photo_path)
    if photo_reader:
        try:
            c.drawImage(photo_reader, photo_x + 50, table_top - 80, width=photo_size, height=photo_size, mask='auto')
        except Exception:
            c.setFont('Helvetica', 9)
            c.setFillColor(colors.red)
            c.drawString(photo_x + 50, table_top - 80, "[Photo error]")

    y = y_table - 10
    # --- Disclaimers ---
    c.setFont('Helvetica-Bold', 12)
    c.setFillColor(colors.HexColor('#1976d2'))
    c.drawString(left, y, "Declaration:")
    y -= line_gap

    declarations = [
        disclaimer1_text,
        disclaimer2_text
    ]
    bullet_radius = 2  # radius of the bullet
    bullet_indent = 16  # space after bullet
    wrap_width = right - left - 10

    c.setFont('Helvetica', 11)
    c.setFillColor(colors.HexColor('#111'))
    for decl in declarations:
        words = decl.split()
        line = ""
        first_line = True
        for word in words:
            test_line = (line + " " + word) if line else word
            available_width = wrap_width - (bullet_indent if not first_line else 0)
            if stringWidth(test_line, 'Helvetica', 11) <= available_width:
                line = test_line
            else:
                # Draw the line
                if first_line:
                    # Draw bullet
                    c.setFillColor(colors.HexColor('#111'))
                    c.circle(left + bullet_radius, y + 4, bullet_radius, fill=1)
                    c.setFillColor(colors.HexColor('#111'))
                    c.drawString(left + bullet_indent, y, line)
                    first_line = False
                else:
                    c.drawString(left + bullet_indent, y, line)
                y -= line_gap - 6
                line = word
        # Draw the last line
        if line:
            if first_line:
                c.setFillColor(colors.HexColor('#111'))
                c.circle(left + bullet_radius, y + 4, bullet_radius, fill=1)
                c.setFillColor(colors.HexColor('#111'))
                c.drawString(left + bullet_indent, y, line)
            else:
                c.drawString(left + bullet_indent, y, line)
            y -= line_gap
    y -= 10
    # --- Yours sincerely and Authorized Signature ---
    c.setFont('Helvetica', 11)
    c.setFillColor(colors.HexColor('#111'))
    c.drawString(left, y, "Yours sincerely,")
    c.drawRightString(right, y, "Authorized Signature")
    y -= 50

    # User signature (left)
    sign_reader = file_utils.get_image_reader(signature_path)
    if sign_reader:
        try:
            c.drawImage(sign_reader, left, y, width=80, height=40, mask='auto')
        except Exception:
            c.setFont('Helvetica', 10)
            c.drawString(left, y, "[Signature load error]")

    # Admin signature (right)
    auth_reader = file_utils.get_image_reader(auth_signature_path)
    if auth_reader:
        try:
            c.drawImage(auth_reader, right-80, y, width=80, height=40, mask='auto')
        except Exception:
            c.setFont('Helvetica', 10)
            c.drawRightString(right, y, "[Auth Signature error]")

    y -= 30
    c.setFont('Helvetica', 10)
    c.setFillColor(colors.HexColor('#555'))
    c.drawString(left, y, name)
    c.save() 