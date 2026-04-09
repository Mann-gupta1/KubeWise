import Link from "next/link";

const steps = [
  {
    href: "/metrics",
    title: "Prometheus → metrics",
    body: "Time series from PromQL (cluster, local node_exporter, or demo data). See API /docs.",
  },
  {
    href: "/recommendations",
    title: "Inefficiency + autoscale",
    body: "Over/under-provisioning rules and replica / CPU recommendations with confidence scores.",
  },
  {
    href: "/cost",
    title: "Cost engine",
    body: "vCPU / GiB-hour pricing, current vs optimized, savings by deployment.",
  },
  {
    href: "/simulations",
    title: "Simulations",
    body: "Traffic spike, node failure, and scale-response scenarios with projected impact.",
  },
];

export default function PipelineOverview() {
  return (
    <div className="rounded-xl border border-emerald-800/40 bg-emerald-950/20 px-4 py-3 sm:px-5">
      <p className="text-xs font-semibold uppercase tracking-wide text-emerald-400/90">
        Intelligence pipeline (backend)
      </p>
      <p className="text-sm text-gray-400 mt-1 mb-3">
        This app is not only an overview chart: the API runs detection, recommendations, cost
        estimation, and simulations. Open each tab for the full demo.
      </p>
      <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
        {steps.map((s) => (
          <li key={s.href}>
            <Link
              href={s.href}
              className="text-emerald-300 hover:text-emerald-200 font-medium underline-offset-2 hover:underline"
            >
              {s.title}
            </Link>
            <span className="text-gray-500"> — </span>
            <span className="text-gray-400">{s.body}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
