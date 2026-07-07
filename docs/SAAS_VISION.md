# SaaS Vision

> **Legacy / future-scope note**
>
> This document is not the current foundation MVP source of truth.
> It may describe future modules, historical plans, or expanded-scope ideas.
> Current foundation MVP source of truth: `STATE.md`, `AGENTS.md`, `docs/00_index.md`, `docs/MVP_SCOPE.md`, `docs/DATA_MODEL.md`, `docs/PIPELINES_SPEC.md`.
> Do not treat API/UI/render/video/autoposting/external analytics/Trend Radar/automatic insight-to-idea loops as current scope unless a future Architecture Gate explicitly reactivates them.

## 1. Назначение документа

Этот документ описывает будущую SaaS-перспективу платформы **Content Plant**.

Он фиксирует:

- зачем Content Plant может стать SaaS-продуктом;
- кто может быть будущим пользователем;
- какие SaaS-функции потенциально нужны;
- какие архитектурные требования нужно учитывать заранее;
- что не входит в MVP;
- какие условия должны быть выполнены до перехода к SaaS;
- как не смешивать внутренний MVP и будущую коммерческую версию.

Документ не является MVP scope.  
Он описывает направление развития после проверки внутренней версии.

---

## 2. Главный принцип

SaaS-слой должен быть **архитектурно предусмотрен, но продуктово отложен**.

Это значит:

- data model должен учитывать Workspace и Project;
- project-level данные должны быть изолированы;
- Brand Profile должен быть универсальным;
- templates должны быть reusable;
- integrations должны быть capability-based;
- но публичная регистрация, биллинг, тарифы и команды не входят в MVP.

Правильный подход:

```text
Build internal multi-project platform first
→ prove production loop
→ collect internal cases
→ package into SaaS later
```

Неправильный подход:

```text
Build public SaaS shell first
→ postpone core production loop
→ get красивый кабинет без работающего завода
```

---

## 3. Почему SaaS-перспектива существует

Content Plant может стать самостоятельным продуктом, если внутренняя версия докажет, что она:

- ускоряет производство контента;
- снижает ручную операционную нагрузку;
- помогает тестировать больше гипотез;
- связывает контент с результатами;
- помогает принимать решения по форматам и темам;
- позволяет переиспользовать один pipeline для разных проектов;
- создаёт repeatable content system.

Главная SaaS-гипотеза:

```text
Small teams and solo operators need a structured content production system,
not just another generator of isolated posts.
```

---

## 4. Внутренний MVP vs Future SaaS

### 4.1. Internal MVP

Internal MVP предназначен для владельца внутренних проектов.

Фокус:

- project switcher;
- Brand Profile;
- Idea Bank;
- Scenario Studio;
- Asset Library;
- Production Engine;
- QA and Review;
- Export-first Publishing;
- manual / CSV metrics;
- basic Analytics;
- feedback loop.

Internal MVP может работать с одним внутренним пользователем.

### 4.2. Future SaaS

Future SaaS предназначен для внешних пользователей и команд.

Фокус:

- public onboarding;
- workspaces;
- teams;
- roles;
- billing;
- usage limits;
- template library;
- integrations management;
- support workflows;
- scalable storage;
- multi-tenant security;
- customer-facing analytics.

Future SaaS не должен ломать внутреннюю модель.  
Он должен вырасти поверх проверенного production loop.

---

## 5. Потенциальные пользователи SaaS

Будущие пользователи Content Plant могут включать:

```text
solo founders
small business owners
marketers
content teams
creators
coaches
education projects
e-commerce teams
agencies
niche media teams
consultants
community operators
```

Общий признак:

> Пользователь регулярно производит контент для продвижения продукта, услуги, экспертизы или медиа и хочет управлять этим как системой.

---

## 6. Потенциальные use cases

### 6.1. Solo founder

Создаёт контент для собственного продукта.

Нужны:

- быстрый Idea → Content pipeline;
- минимум ручной рутины;
- понятный dashboard;
- простой export;
- метрики и выводы.

### 6.2. Small business

Продвигает услуги или товары через органический контент.

Нужны:

- brand consistency;
- reusable content formats;
- platform adaptation;
- publishing calendar;
- lead / conversion tracking.

### 6.3. E-commerce

Создаёт продуктовые объяснения, подборки, short videos и posts.

Нужны:

- product catalog integration later;
- product-focused templates;
- CTA and link tracking;
- performance by product/category.

### 6.4. Education project

Создаёт объясняющий контент, lessons, carousels, short videos.

Нужны:

- explainer formats;
- lesson-to-content repurpose;
- topic taxonomy;
- funnel stages;
- course CTA tracking.

### 6.5. Agency

Управляет контентом нескольких клиентов.

Нужны:

- multiple workspaces or client projects;
- roles and approvals;
- client-ready reporting;
- reusable templates;
- brand separation.

---

## 7. SaaS product positioning

Возможное позиционирование:

```text
Content Plant helps small teams build repeatable AI-assisted content production systems:
from trend and idea to scenario, assets, publishing package, metrics and next recommendations.
```

Не позиционировать как:

- simple post generator;
- simple video editor;
- simple autoposter;
- simple prompt pack;
- generic AI copywriting tool.

Content Plant должен позиционироваться как:

```text
Content operations system
AI-assisted content factory
Brand-aware production workflow
Content feedback loop platform
```

---

## 8. SaaS capabilities map

Future SaaS may include:

```text
Public signup
Workspace onboarding
Project creation wizard
Brand Profile wizard
Template library
Content format presets
Team roles
Approval workflows
Billing and plans
Usage limits
Integrations marketplace
Customer support
Knowledge base
Public API
White-label options
Agency client mode
```

Эти capabilities не входят в MVP, если явно не перенесены в roadmap отдельным решением.

---

## 9. Multi-tenant architecture principles

Future SaaS потребует multi-tenant architecture.

Главные требования:

- Workspace isolation;
- Project isolation;
- user access control;
- secure credential storage;
- per-workspace usage limits;
- audit logs;
- scalable file storage;
- background job isolation;
- integration permission boundaries;
- data export;
- deletion policies.

MVP может использовать один internal workspace, но данные должны быть спроектированы так, чтобы multi-tenant слой можно было добавить позже.

---

## 10. Workspace model future

В SaaS Workspace может соответствовать:

```text
individual account
company
agency
client organization
team
```

Workspace может содержать несколько Projects.

```text
Workspace
  → Project A
  → Project B
  → Project C
```

В MVP Workspace может быть один:

```text
workspace_id = internal
```

Но `workspace_id` желательно иметь в ключевых сущностях.

---

## 11. User and role model future

Future SaaS roles may include:

```text
owner
admin
strategist
editor
reviewer
analyst
client_viewer
```

### owner

Управляет workspace, billing, users, integrations.

### admin

Управляет projects, settings and workflows.

### strategist

Создаёт идеи, стратегии, форматы.

### editor

Работает со сценариями, текстами и ассетами.

### reviewer

Утверждает контент.

### analyst

Работает с метриками и рекомендациями.

### client_viewer

Смотрит отчёты и approved content.

MVP не требует этих ролей.

---

## 12. SaaS onboarding future

Future onboarding may include:

```text
Create account
Create workspace
Create first project
Fill Brand Profile
Choose content goals
Select platforms
Choose content formats
Upload brand assets
Create first idea
Generate first scenario
Render or export first content item
```

Но MVP не должен строиться вокруг public onboarding wizard.

---

## 13. Billing future

Future billing may include:

- free trial;
- subscription plans;
- usage-based render limits;
- storage limits;
- team seats;
- integration limits;
- premium templates;
- agency plans;
- white-label pricing.

Billing is explicitly not part of MVP.

SaaS billing should not be introduced until:

1. internal production loop works;
2. value is proven;
3. key usage metrics are known;
4. cost model is understood;
5. support load is estimated.

---

## 14. Usage limits future

Future SaaS may need limits for:

```text
projects
team members
storage
render minutes
LLM tokens
generated scenarios
exports
scheduled publications
analytics imports
integrations
```

Limits should be based on actual internal usage data, not guessed too early.

---

## 15. Template library future

Future SaaS may include reusable templates:

- production templates;
- scenario templates;
- prompt templates;
- report templates;
- platform caption templates;
- carousel templates;
- pin templates;
- analytics report templates.

Template marketplace is a later concept, not MVP.

---

## 16. Marketplace future

Potential marketplace categories:

```text
content formats
production templates
prompt packs
industry playbooks
analytics report templates
brand profile presets
integration connectors
```

Marketplace should only be considered after:

- templates are stable;
- internal formats work;
- user roles exist;
- quality review process exists;
- licensing and ownership rules are defined.

---

## 17. Integrations future

SaaS version may support broader integrations:

```text
social publishing APIs
analytics APIs
website analytics
CRM
email marketing
ad platforms
product catalogs
stock media libraries
AI generation providers
cloud storage
webhooks
public API
```

Integration expansion should remain capability-based.

A platform can be:

```text
manual_export
csv_import
api_import
semi_auto_publish
auto_publish
disabled
```

Do not promise universal autoposting unless platform capabilities and policy allow it.

---

## 18. Security requirements future

Future SaaS will need:

- authentication;
- authorization;
- secure session management;
- encrypted secrets;
- workspace-level isolation;
- audit logs;
- backup policies;
- data deletion;
- rate limiting;
- abuse prevention;
- file scanning;
- permission checks for exports and integrations.

MVP can avoid many of these by remaining internal, but architecture should not make them impossible.

---

## 19. Data ownership and export future

SaaS users should be able to export:

- projects;
- Brand Profiles;
- ideas;
- scenarios;
- content items;
- publications;
- metrics;
- assets metadata;
- reports.

Raw asset file export may need separate storage and permission rules.

---

## 20. Customer support future

Future SaaS may require:

- support dashboard;
- issue reporting;
- usage diagnostics;
- failed job logs;
- integration status checks;
- customer onboarding guides;
- documentation;
- help center.

These are not part of MVP.

---

## 21. SaaS analytics future

SaaS product analytics should be separate from user content analytics.

### User content analytics

Belongs to user's Projects:

```text
views
clicks
conversions
revenue
content performance
```

### Product analytics

Belongs to Content Plant operators:

```text
activation
retention
feature usage
render volume
export volume
integration usage
failure rates
support load
```

Do not mix these two analytics layers.

---

## 22. SaaS readiness checklist

Before starting SaaS implementation, the following should be true:

1. Internal MVP production loop works end-to-end.
2. At least one project has produced repeated content cycles.
3. Analytics loop produces useful recommendations.
4. Project and Brand Profile separation is stable.
5. Data model supports workspace/project scoping.
6. Production templates are reusable.
7. Export-first publishing works reliably.
8. Render costs and storage costs are understood.
9. Support risks are known.
10. Clear target user segment is selected.

---

## 23. Possible SaaS stages

### Stage 1. Internal tool

One internal workspace.  
Multiple internal projects.  
No external users.

### Stage 2. Private beta

Small number of invited users.  
Manual onboarding.  
No self-serve billing.  
Close support.

### Stage 3. Managed SaaS

External users with workspace onboarding.  
Limited plans.  
Manual support.  
Controlled integrations.

### Stage 4. Self-serve SaaS

Public signup.  
Billing.  
Plans.  
Usage limits.  
Support docs.  
Scalable infrastructure.

### Stage 5. Ecosystem

Marketplace.  
White-label.  
Agency mode.  
Public API.  
Template creators.

---

## 24. MVP boundaries

The following are not part of MVP:

```text
public signup
external user accounts
billing
plans
subscriptions for Content Plant
team roles
permissions
customer onboarding
marketplace
white-label
public API
agency client portal
self-serve SaaS analytics
support center
```

The MVP may include internal placeholders only when they help future compatibility.

---

## 25. Architecture decisions to keep SaaS possible

Even in MVP:

- use `workspace_id` where practical;
- use `project_id` everywhere for project-level entities;
- keep Brand Profile separate from templates;
- keep integrations project-scoped;
- avoid global asset buckets;
- avoid hardcoded project logic;
- separate Content Analytics from Product Analytics;
- make templates reusable;
- keep export/manual fallback;
- store input snapshots for reproducibility;
- keep status transitions explicit.

---

## 26. What should not be optimized too early

Do not optimize too early for:

- complex permissions;
- billing plans;
- marketplace;
- multi-region infrastructure;
- enterprise compliance;
- automated support;
- public template submissions;
- role-specific dashboards;
- public API versioning.

These can become expensive tunnels to nowhere if the production loop is not proven.

---

## 27. Success criteria for SaaS transition

Content Plant is ready to explore SaaS when:

- internal users repeatedly use it for real content production;
- it saves measurable time;
- it improves content output volume or quality;
- analytics influence the next production cycle;
- non-founder users can understand workflows;
- project setup is repeatable;
- at least 2-3 distinct projects work through the same platform model;
- formats are reusable across projects;
- production templates are not project-specific;
- first target customer segment is clear.

---

## 28. Risks

### 28.1. Building SaaS too early

Risk:

```text
The team builds login, billing and account settings before proving content production value.
```

Mitigation:

```text
Keep SaaS features outside MVP until internal loop works.
```

### 28.2. Overpromising integrations

Risk:

```text
Users expect full autoposting and automatic analytics everywhere.
```

Mitigation:

```text
Use capability-based integrations and export-first positioning.
```

### 28.3. Template quality risk

Risk:

```text
Templates work for one internal project but fail for other brands.
```

Mitigation:

```text
Test templates across multiple Brand Profiles before SaaS packaging.
```

### 28.4. Support burden

Risk:

```text
Users struggle with assets, prompts, integrations and platform limits.
```

Mitigation:

```text
Build guided workflows and clear fallback modes before scaling.
```

### 28.5. Cost risk

Risk:

```text
Render, storage and LLM costs exceed pricing assumptions.
```

Mitigation:

```text
Measure internal usage before defining plans.
```

---

## 29. Open questions

1. Which external user segment should be tested first?
2. Should the first external version be managed service or self-serve SaaS?
3. What is the minimum onboarding flow for a non-technical user?
4. What production formats are strong enough for external use?
5. What integrations are must-have for the first paid users?
6. How should pricing account for render, storage and LLM usage?
7. Should agency mode be prioritized before solo-founder mode?
8. Should templates be curated only or user-generated?
9. What data export guarantees should SaaS users receive?
10. What support model is realistic for early SaaS?
