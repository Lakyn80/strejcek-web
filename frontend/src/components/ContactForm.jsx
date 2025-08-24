import React, { useState } from "react";
import { postContact } from "../lib/api.js";

export default function ContactForm() {
  const initialForm = {
    name: "", email: "", phone: "", itemType: "Palety",
    quantity: "", location: "", message: "",
    wantDelivery: false, smallShipper: false, company: ""
  };

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [form, setForm] = useState(initialForm);

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true); setError(null); setResult(null);
    try {
      const data = await postContact(form);
      if (data?.ok) {
        setResult(data?.message || "Odesláno.");
        // reset formuláře
        setForm(initialForm);
        e.currentTarget?.reset?.();
      } else {
        setError(data?.error || "Chyba při odesílání formuláře.");
      }
    } catch (err) {
      setError(err?.response?.data?.error || "Chyba při odesílání formuláře.");
    } finally {
      setLoading(false);
    }
  };

  const onChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((f) => ({ ...f, [name]: type === "checkbox" ? checked : value }));
  };

  return (
    <section id="kontakt" className="py-12">
      <h2 className="text-2xl font-bold mb-6">Kontakt / Poptávka</h2>
      <form onSubmit={submit} className="grid gap-4 bg-white p-5 border rounded-lg">
        <input type="text" name="company" value={form.company} onChange={onChange} className="hidden" tabIndex={-1} autoComplete="off" />
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium">Jméno *</label>
            <input required name="name" value={form.name} onChange={onChange} className="mt-1 w-full border rounded px-3 py-2" placeholder="Vaše jméno" />
          </div>
          <div>
            <label className="block text-sm font-medium">E-mail *</label>
            <input required type="email" name="email" value={form.email} onChange={onChange} className="mt-1 w-full border rounded px-3 py-2" placeholder="vas@email.cz" />
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium">Telefon</label>
            <input name="phone" value={form.phone} onChange={onChange} className="mt-1 w-full border rounded px-3 py-2" placeholder="+420..." />
          </div>
          <div>
            <label className="block text-sm font-medium">Poptávám</label>
            <select name="itemType" value={form.itemType} onChange={onChange} className="mt-1 w-full border rounded px-3 py-2">
              <option>Palety</option><option>Big-bagy</option><option>Krabice</option>
            </select>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium">Množství / Objem</label>
            <input name="quantity" value={form.quantity} onChange={onChange} className="mt-1 w-full border rounded px-3 py-2" placeholder="např. 50 ks, 5 big-bagů..." />
          </div>
          <div>
            <label className="block text-sm font-medium">Lokalita (PSČ / obec)</label>
            <input name="location" value={form.location} onChange={onChange} className="mt-1 w-full border rounded px-3 py-2" placeholder="např. 686 01 Uherské Hradiště" />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium">Zpráva *</label>
          <textarea required name="message" value={form.message} onChange={onChange} className="mt-1 w-full border rounded px-3 py-2 min-h-[120px]" placeholder="Vaše upřesnění..." />
        </div>

        <div className="flex items-center gap-6">
          <label className="inline-flex items-center gap-2">
            <input type="checkbox" name="wantDelivery" checked={form.wantDelivery} onChange={onChange} />
            <span>Chci nacenit dovoz</span>
          </label>
          <label className="inline-flex items-center gap-2">
            <input type="checkbox" name="smallShipper" checked={form.smallShipper} onChange={onChange} />
            <span>Jsem malý odběratel – chci zaslání poštou (hradím poštovné)</span>
          </label>
        </div>

        <div className="flex items-center gap-3">
          <button disabled={loading} type="submit" className="bg-gray-900 text-white px-5 py-3 rounded disabled:opacity-60">
            {loading ? "Odesílám…" : "Odeslat poptávku"}
          </button>
          {result && <span className="text-green-600">{result}</span>}
          {error && <span className="text-red-600">{error}</span>}
        </div>

        <p className="text-xs text-gray-500">Ceny jsou orientační a upřesníme je dle objemu a vzdálenosti.</p>
      </form>
    </section>
  );
}
