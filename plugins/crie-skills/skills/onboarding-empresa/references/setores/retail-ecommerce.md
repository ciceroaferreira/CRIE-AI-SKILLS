---
code: retail-ecommerce
name: Retail and e-commerce (stores, boutiques, online shops, Amazon/Etsy/eBay sellers, Shopify brands)
name_pt: Varejo e e-commerce (lojas, boutiques, lojas online, vendedores Amazon/Etsy/eBay, marcas Shopify)
suggested_level: standard
---

## How the business works
- Revenue: in-store sales, own online store (Shopify, Square Online, WooCommerce), marketplaces (Amazon, Etsy, eBay, Walmart), social commerce (Instagram, TikTok Shop), wholesale.
- Costs: cost of goods (often 40–60% of price), shipping and packaging, marketplace fees (Amazon referral ~8–15% + FBA fees; Etsy ~6.5% transaction + payment processing ~3% + listing fees; Shopify plan + ~2.9% + 30¢ — confirm current pricing), card processing (~2.6–3.5%), returns, ads, rent.
- Seasonality: Valentine's Day, Mother's Day, Back to School, Black Friday/Cyber Monday, Small Business Saturday, holiday season (often 30%+ of the year).
- Winners: know margin per SKU after all fees, turn inventory fast, own their customer list (email/SMS), and keep great reviews.

## Key metrics
- Gross margin per SKU after fees, shipping and returns
- Inventory turnover and days of stock; dead stock value
- Conversion rate and average order value (AOV)
- Customer acquisition cost (CAC) and return on ad spend (ROAS)
- Repeat purchase rate and email/SMS list growth
- Return rate and reason; rating on marketplaces/Google

## Regulation, confidentiality and risks
- Sales tax: collect where you have physical or economic nexus (post-Wayfair thresholds, often $100,000 in sales per state — verify each state); marketplace facilitators (Amazon, Etsy, eBay, Walmart) collect and remit on their sales in most states, but your own site is on you. Register, collect at checkout on top of the price, file on time.
- FTC Mail, Internet or Telephone Order Rule: ship within the time you state (or 30 days), notify delays and offer cancellation/refund.
- No general federal right to return: your return policy is your choice but must be clearly disclosed; some states require posting it (e.g., CA, NY, FL).
- PCI-DSS for card data (use hosted checkout; never store full card numbers). CAN-SPAM for email (unsubscribe, address); TCPA for marketing texts (prior express written consent).
- FTC rule banning fake reviews and testimonials (2024) and Endorsement Guides (#ad for influencers). Product safety (CPSC, especially kids' products) and labeling rules.
- Customer lists with addresses and purchase history → `standard`, or `elevated` for large lists.

## Persona adjustments
- **Otávio (Operations)** owns inventory, reorder points, fulfillment, shipping rates and returns.
- **Ana (Finance)** calculates margin per SKU per channel after all fees and tracks sales tax collected vs. owed.
- **Marina (Marketing)** focuses on product pages, email/SMS flows, Instagram/TikTok and seasonal campaigns, within FTC review and endorsement rules.
- **Carlos (Sales)** handles wholesale accounts, marketplaces and B2B pricing.
- **Juliana (Legal)** keeps return/shipping policies, privacy policy and terms consistent across channels.

## Specialist personas
- **Lívia — E-commerce & marketplaces**: call me when you want better listings, to choose channels or to fix conversion. Frameworks: listing optimization (title, photos, keywords, bullets), channel profitability matrix, abandoned cart and post-purchase flows. First deliverables: rewrite of the top 10 listings; channel margin comparison; 3 email flows (welcome, abandoned cart, post-purchase). Limits: platform rules change often — check each marketplace's current policies.

## Routines Claude can run
- Product descriptions and listings for site and marketplaces (EN and PT if needed)
- Margin per SKU and per channel from a sales export
- Reorder report from an inventory spreadsheet (reorder point, slow movers, dead stock)
- Seasonal campaign plan following the US retail calendar
- Replies to reviews and customer service emails (shipping delays, returns)
- Weekly sales report (sales, AOV, conversion, top products)
- Return/shipping policy and FAQ drafts
- Sales tax checklist by state (nexus, registration, filing dates) to confirm with the CPA

## Extra onboarding questions
- Where do you sell (store, own site, Amazon, Etsy, eBay, Instagram/TikTok, wholesale)?
- How do you track inventory today?
- In which states do you collect sales tax?
- What are your best-selling and most profitable products?
