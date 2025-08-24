import html

def build_email_bodies(data: dict, ip: str, ua: str, when: str) -> tuple[str, str]:
    name = html.escape(data.get("name", ""))
    email = html.escape(data.get("email", ""))
    phone = html.escape(data.get("phone", ""))
    item = html.escape(data.get("itemType", ""))
    quantity = html.escape(data.get("quantity", ""))
    location = html.escape(data.get("location", ""))
    message = html.escape(data.get("message", ""))
    want_delivery = "Ano" if data.get("wantDelivery") else "Ne"
    small_shipper = "Ano" if data.get("smallShipper") else "Ne"

    html_body = f"""        <h2>Nová poptávka</h2>
    <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">
      <tr><th align="left">Jméno</th><td>{name}</td></tr>
      <tr><th align="left">E-mail</th><td>{email}</td></tr>
      <tr><th align="left">Telefon</th><td>{phone}</td></tr>
      <tr><th align="left">Poptávám</th><td>{item}</td></tr>
      <tr><th align="left">Množství/Objem</th><td>{quantity}</td></tr>
      <tr><th align="left">Lokalita</th><td>{location}</td></tr>
      <tr><th align="left">Chci nacenit dovoz</th><td>{want_delivery}</td></tr>
      <tr><th align="left">Malý odběratel – zaslání poštou</th><td>{small_shipper}</td></tr>
      <tr><th align="left">Zpráva</th><td><pre style="white-space:pre-wrap">{message}</pre></td></tr>
    </table>
    <p style="color:#666;font-size:12px;margin-top:16px;">
      Odesláno: {when}<br>
      IP: {ip}<br>
      Prohlížeč: {html.escape(ua)}
    </p>
    """

    text_body = f"""        Nová poptávka

    Jméno: {name}
    E-mail: {email}
    Telefon: {phone}
    Poptávám: {item}
    Množství/Objem: {quantity}
    Lokalita: {location}
    Chci nacenit dovoz: {want_delivery}
    Malý odběratel – zaslání poštou: {small_shipper}

    Zpráva:
    {message}

    ---
    Odesláno: {when}
    IP: {ip}
    UA: {ua}
    """
    return html_body, text_body
