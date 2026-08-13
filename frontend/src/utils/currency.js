const CURRENCY_SYMBOLS = {
  USD: "$",
  EUR: "€",
  GBP: "£",
  JPY: "¥",
};

// JPY has no minor/decimal subunit in everyday use.
const ZERO_DECIMAL_CURRENCIES = new Set(["JPY"]);

export function currencySymbol(code) {
  return CURRENCY_SYMBOLS[code] || `${code} `;
}

export function currencyDecimals(code) {
  return ZERO_DECIMAL_CURRENCIES.has(code) ? 0 : 2;
}

export function formatCurrency(amount, code = "USD") {
  return `${currencySymbol(code)}${Number(amount).toFixed(currencyDecimals(code))}`;
}

// Groups a list of accounts by currency, summing balances.
// Returns [{ currency, total }], sorted with USD first when present.
export function groupBalancesByCurrency(accounts) {
  const totals = new Map();
  for (const account of accounts) {
    const code = account.currency || "USD";
    totals.set(code, (totals.get(code) || 0) + account.balance);
  }
  return Array.from(totals.entries())
    .map(([currency, total]) => ({ currency, total }))
    .sort((a, b) => (a.currency === "USD" ? -1 : b.currency === "USD" ? 1 : a.currency.localeCompare(b.currency)));
}
