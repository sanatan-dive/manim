import Header from "../components/Header";
import Footer from "../components/Footer";
import { Book, MessagesSquare, Video } from "lucide-react";

const supportLinks = [
  {
    name: "Documentation",
    href: "#",
    description:
      "Detailed guides on how to use the generation tools, prompt engineering, and animation export settings.",
    icon: Book,
  },

  {
    name: "Video Tutorials",
    href: "#",
    description:
      "Watch step-by-step tutorials on creating math animations from simple to complex.",
    icon: Video,
  },
  {
    name: "Community Forum",
    href: "#",
    description:
      "Connect with other users, share your creations, and get help from the community.",
    icon: MessagesSquare,
  },
];

export default function Help() {
  return (
    <div className="bg-stone-50 min-h-screen pt-24 pb-12 transition-colors duration-300">
      <Header />
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center mb-16">
          <h2 className="text-base font-semibold leading-7 text-stone-600 uppercase tracking-wide">
            Support Center
          </h2>
          <p className="mt-2 text-4xl font-medium tracking-tight text-stone-900 sm:text-5xl font-funnel">
            Everything you need to master Manim GenAI
          </p>
          <p className="mt-6 text-lg leading-8 text-stone-600 font-funnel">
            Whether you're new to AI animation or an experienced developer, we
            have the resources to help you succeed.
          </p>
        </div>
        
        <div className="mx-auto max-w-2xl lg:max-w-none">
          <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-16 lg:max-w-none lg:grid-cols-2">
            {supportLinks.map((link) => (
              <div key={link.name} className="flex flex-col bg-white p-8 rounded-2xl shadow-sm border border-stone-100 hover:shadow-md transition-shadow">
                <dt className="flex items-center gap-x-3 text-lg font-semibold leading-7 text-stone-900 font-funnel">
                  <div className="p-2 bg-stone-100 rounded-lg">
                    <link.icon
                      className="h-5 w-5 flex-none text-stone-900"
                      aria-hidden="true"
                    />
                  </div>
                  {link.name}
                </dt>
                <dd className="mt-4 flex flex-auto flex-col text-base leading-7 text-stone-600 font-funnel">
                  <p className="flex-auto">{link.description}</p>
                  <p className="mt-6">
                    <a
                      href={link.href}
                      className="text-sm font-semibold leading-6 text-stone-900 hover:text-stone-600 flex items-center gap-1 group transition-colors"
                    >
                      Learn more <span aria-hidden="true" className="group-hover:translate-x-1 transition-transform">→</span>
                    </a>
                  </p>
                </dd>
              </div>
            ))}
          </dl>
        </div>
      </div>
      <Footer />
    </div>
  );
}
