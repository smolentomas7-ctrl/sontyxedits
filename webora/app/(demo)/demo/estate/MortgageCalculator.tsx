"use client";

import { useMemo, useState } from "react";
import { Info } from "lucide-react";

/**
 * Standard annuity payment:
 *   M = P · r / (1 − (1 + r)^−n)
 * where r is the monthly rate and n the number of payments. With a zero
 * interest rate the formula degenerates, so that case is handled separately.
 */
function monthlyPayment(principal: number, annualRatePercent: number, years: number): number {
  const n = years * 12;
  if (n <= 0) return 0;
  const r = annualRatePercent / 100 / 12;
  if (r === 0) return principal / n;
  return (principal * r) / (1 - Math.pow(1 + r, -n));
}

const eur = new Intl.NumberFormat("sk-SK", {
  style: "currency",
  currency: "EUR",
  maximumFractionDigits: 0,
});

export function MortgageCalculator({ defaultPrice = 450000 }: { defaultPrice?: number }) {
  const [price, setPrice] = useState(defaultPrice);
  const [downPercent, setDownPercent] = useState(20);
  const [years, setYears] = useState(30);
  const [rate, setRate] = useState(4.2);

  const { deposit, loan, payment, totalPaid, overpayment } = useMemo(() => {
    const depositValue = Math.round((price * downPercent) / 100);
    const loanValue = Math.max(0, price - depositValue);
    const paymentValue = monthlyPayment(loanValue, rate, years);
    const total = paymentValue * years * 12;
    return {
      deposit: depositValue,
      loan: loanValue,
      payment: paymentValue,
      totalPaid: total,
      overpayment: total - loanValue,
    };
  }, [price, downPercent, years, rate]);

  return (
    <div className="rounded-xl border border-[#D9E0E8] bg-white p-7">
      <h3 className="font-[family-name:var(--font-space-grotesk)] text-xl font-bold text-[#0E2A47]">
        Hypotekárna kalkulačka
      </h3>
      <p className="mt-2 text-[15px] text-[#5B6977]">
        Orientačný výpočet mesačnej splátky pri anuitnom splácaní.
      </p>

      <div className="mt-7 flex flex-col gap-6">
        <div>
          <label
            htmlFor="mc-price"
            className="mb-2 flex items-baseline justify-between text-[14px] font-medium text-[#5B6977]"
          >
            Cena nehnuteľnosti
            <span className="font-[family-name:var(--font-space-grotesk)] text-[16px] font-bold text-[#0E2A47]">
              {eur.format(price)}
            </span>
          </label>
          <input
            id="mc-price"
            type="range"
            min={80000}
            max={1200000}
            step={10000}
            value={price}
            onChange={(event) => setPrice(Number(event.target.value))}
            className="w-full accent-[#1A8152]"
          />
        </div>

        <div>
          <label
            htmlFor="mc-down"
            className="mb-2 flex items-baseline justify-between text-[14px] font-medium text-[#5B6977]"
          >
            Vlastné zdroje
            <span className="font-[family-name:var(--font-space-grotesk)] text-[16px] font-bold text-[#0E2A47]">
              {downPercent} % · {eur.format(deposit)}
            </span>
          </label>
          <input
            id="mc-down"
            type="range"
            min={0}
            max={60}
            step={5}
            value={downPercent}
            onChange={(event) => setDownPercent(Number(event.target.value))}
            className="w-full accent-[#1A8152]"
          />
        </div>

        <div className="grid gap-6 sm:grid-cols-2">
          <div>
            <label
              htmlFor="mc-years"
              className="mb-2 flex items-baseline justify-between text-[14px] font-medium text-[#5B6977]"
            >
              Splatnosť
              <span className="font-bold text-[#0E2A47]">{years} r.</span>
            </label>
            <input
              id="mc-years"
              type="range"
              min={5}
              max={40}
              step={1}
              value={years}
              onChange={(event) => setYears(Number(event.target.value))}
              className="w-full accent-[#1A8152]"
            />
          </div>

          <div>
            <label
              htmlFor="mc-rate"
              className="mb-2 flex items-baseline justify-between text-[14px] font-medium text-[#5B6977]"
            >
              Úrok
              <span className="font-bold text-[#0E2A47]">
                {rate.toFixed(1).replace(".", ",")} %
              </span>
            </label>
            <input
              id="mc-rate"
              type="range"
              min={0}
              max={9}
              step={0.1}
              value={rate}
              onChange={(event) => setRate(Number(event.target.value))}
              className="w-full accent-[#1A8152]"
            />
          </div>
        </div>
      </div>

      <div className="mt-8 rounded-lg bg-[#F3F7FB] p-6">
        <p className="text-[13px] font-medium uppercase tracking-[0.1em] text-[#5B6977]">
          Mesačná splátka
        </p>
        <p
          aria-live="polite"
          className="mt-1.5 font-[family-name:var(--font-space-grotesk)] text-4xl font-bold text-[#17457A]"
        >
          {eur.format(Math.round(payment))}
        </p>

        <dl className="mt-5 flex flex-col gap-2 border-t border-[#D9E0E8] pt-4 text-[14px]">
          <div className="flex justify-between gap-4">
            <dt className="text-[#5B6977]">Výška úveru</dt>
            <dd className="font-medium text-[#0E2A47]">{eur.format(loan)}</dd>
          </div>
          <div className="flex justify-between gap-4">
            <dt className="text-[#5B6977]">Zaplatíte spolu</dt>
            <dd className="font-medium text-[#0E2A47]">{eur.format(Math.round(totalPaid))}</dd>
          </div>
          <div className="flex justify-between gap-4">
            <dt className="text-[#5B6977]">Preplatíte</dt>
            <dd className="font-medium text-[#0E2A47]">{eur.format(Math.round(overpayment))}</dd>
          </div>
        </dl>
      </div>

      <p className="mt-5 flex gap-2 text-[13px] leading-relaxed text-[#5B6977]">
        <Info aria-hidden="true" strokeWidth={1.5} className="mt-0.5 size-4 shrink-0 text-[#17457A]" />
        Ide o orientačný prepočet, nie o ponuku banky. Nezahŕňa poplatky, poistenie ani
        posúdenie bonity. Skutočné podmienky vám potvrdí banka.
      </p>
    </div>
  );
}
