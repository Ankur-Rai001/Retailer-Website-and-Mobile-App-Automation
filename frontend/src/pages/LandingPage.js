import { motion } from 'framer-motion';
import { Store, Zap, TrendingUp, Globe, IndianRupee, Smartphone, Package, BarChart3, Users, Check } from 'lucide-react';
import { Button } from '../components/ui/button';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function LandingPage() {
  const handleLogin = () => {
    const redirectUrl = window.location.origin + '/dashboard';
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  const handleDemoClick = () => {
    window.location.href = '/demo-login';
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      <nav className="sticky top-0 z-50 backdrop-blur-xl bg-white/80 border-b border-slate-200/50">
        <div className="max-w-7xl mx-auto px-6 md:px-12 lg:px-24 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Store className="h-8 w-8 text-primary" />
              <span className="font-heading text-2xl font-bold text-secondary">ShopSwift India</span>
            </div>
            <Button 
              onClick={handleLogin}
              data-testid="login-button"
              className="bg-primary text-white hover:bg-primary/90 rounded-full px-6 py-5 font-semibold shadow-lg transition-all hover:shadow-xl hover:-translate-y-0.5"
            >
              Get Started Free
            </Button>
          </div>
        </div>
      </nav>

      <section className="relative overflow-hidden px-6 md:px-12 lg:px-24 pt-20 pb-32">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <div className="inline-block px-4 py-2 bg-primary/10 rounded-full mb-6">
                <span className="text-primary font-semibold text-sm">Zero Transaction Fees</span>
              </div>
              <h1 className="text-5xl md:text-7xl font-bold tracking-tight leading-[1.1] text-secondary mb-6">
                Your Shop,<br />Online in<br />
                <span className="text-primary">One Click</span>
              </h1>
              <p className="text-xl text-slate-600 mb-8 leading-relaxed">
                Create your professional online store instantly. No coding, no setup hassles. 
                <span className="font-semibold text-secondary"> Keep 100% of your profits</span> - only ₹99/month!
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Button 
                  onClick={handleLogin}
                  data-testid="hero-cta-button"
                  className="bg-primary text-white hover:bg-primary/90 rounded-full px-8 py-6 text-lg font-semibold shadow-lg transition-all hover:shadow-xl hover:-translate-y-1"
                >
                  Start Your Store Now
                </Button>
                <Button 
                  variant="outline"
                  className="bg-white text-secondary border-2 border-slate-200 hover:border-secondary rounded-full px-8 py-6 text-lg font-medium transition-all"
                >
                  See How It Works
                </Button>
              </div>
              <div className="mt-8 flex items-center gap-6">
                <div className="flex -space-x-2">
                  {[1,2,3,4].map(i => (
                    <div key={i} className="w-10 h-10 rounded-full bg-slate-200 border-2 border-white"></div>
                  ))}
                </div>
                <p className="text-sm text-slate-600"><span className="font-semibold text-secondary">2,500+</span> retailers already online</p>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="relative"
            >
              <img 
                src="https://images.unsplash.com/photo-1672335468275-e79517ae9f95?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA2OTV8MHwxfHNlYXJjaHw0fHxpbmRpYW4lMjBzaG9wa2VlcGVyJTIwc21pbGluZyUyMGtpcmFuYSUyMHN0b3JlfGVufDB8fHx8MTc2OTA4MDkxN3ww&ixlib=rb-4.1.0&q=85"
                alt="Happy Indian shopkeeper"
                className="rounded-2xl shadow-2xl"
              />
              <div className="absolute -bottom-6 -left-6 bg-white p-6 rounded-xl shadow-xl border border-slate-100">
                <p className="text-sm text-muted mb-1">Monthly Revenue</p>
                <p className="text-3xl font-bold text-accent">₹45,000</p>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      <section className="px-6 md:px-12 lg:px-24 py-24 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-secondary mb-4">Why Shopkeepers Love Us</h2>
            <p className="text-xl text-slate-600">Everything you need to succeed online</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              { icon: IndianRupee, title: "Zero Commission", desc: "Unlike others, we don't take a cut. Keep every rupee you earn." },
              { icon: Zap, title: "Instant Setup", desc: "AI creates your complete store in under 2 minutes. No technical knowledge needed." },
              { icon: Smartphone, title: "Mobile App Included", desc: "Get your branded Android/iOS app automatically. Reach customers everywhere." },
              { icon: Package, title: "Inventory Management", desc: "Track stock, get low-stock alerts, manage products with ease." },
              { icon: BarChart3, title: "Sales Analytics", desc: "Understand your business with simple, powerful insights." },
              { icon: Globe, title: "Custom Domain", desc: "Use your own domain (mybusiness.com) or free subdomain (myshop.shopswift.in)." },
            ].map((feature, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
                viewport={{ once: true }}
                className="bg-white border border-slate-100 shadow-sm hover:shadow-md transition-all p-8 rounded-2xl"
              >
                <feature.icon className="h-12 w-12 text-primary mb-4" />
                <h3 className="text-xl font-semibold text-secondary mb-2">{feature.title}</h3>
                <p className="text-slate-600">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <section className="px-6 md:px-12 lg:px-24 py-24 bg-gradient-to-br from-primary/5 to-accent/5">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-secondary mb-4">Simple, Honest Pricing</h2>
            <p className="text-xl text-slate-600">No hidden fees. No surprises.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {[
              { name: "Trial", price: "Free", period: "7 days", features: ["Full features access", "Up to 20 products", "Basic support", "shopswift.in subdomain"] },
              { name: "Basic", price: "₹99", period: "per month", features: ["Unlimited products", "Custom domain support", "Priority support", "GST invoicing", "UPI/Card payments"], popular: true },
              { name: "Premium", price: "₹299", period: "per month", features: ["Everything in Basic", "Premium templates", "ONDC integration", "SEO optimization", "Marketing tools"] },
            ].map((plan, idx) => (
              <div
                key={idx}
                className={`bg-white border-2 ${plan.popular ? 'border-primary shadow-xl scale-105' : 'border-slate-200 shadow-sm'} rounded-2xl p-8 relative`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-primary text-white px-4 py-1 rounded-full text-sm font-semibold">
                    Most Popular
                  </div>
                )}
                <h3 className="text-2xl font-bold text-secondary mb-2">{plan.name}</h3>
                <div className="mb-6">
                  <span className="text-4xl font-bold text-secondary">{plan.price}</span>
                  <span className="text-slate-600 ml-2">{plan.period}</span>
                </div>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((f, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <Check className="h-5 w-5 text-accent flex-shrink-0 mt-0.5" />
                      <span className="text-slate-600">{f}</span>
                    </li>
                  ))}
                </ul>
                <Button 
                  onClick={handleLogin}
                  className={`w-full rounded-full py-5 font-semibold ${plan.popular ? 'bg-primary text-white hover:bg-primary/90' : 'bg-slate-100 text-secondary hover:bg-slate-200'}`}
                >
                  Get Started
                </Button>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="px-6 md:px-12 lg:px-24 py-32 bg-secondary text-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-6xl font-bold mb-6">Ready to Go Online?</h2>
          <p className="text-xl text-slate-300 mb-8">Join thousands of Indian retailers already growing their business online</p>
          <Button 
            onClick={handleLogin}
            data-testid="footer-cta-button"
            className="bg-primary text-white hover:bg-primary/90 rounded-full px-8 py-6 text-lg font-semibold shadow-lg transition-all hover:shadow-xl hover:-translate-y-1"
          >
            Create Your Store - Free Trial
          </Button>
          <p className="text-sm text-slate-400 mt-4">No credit card required. Start selling in 5 minutes.</p>
        </div>
      </section>

      <footer className="px-6 md:px-12 lg:px-24 py-12 bg-slate-900 text-slate-400">
        <div className="max-w-7xl mx-auto text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Store className="h-6 w-6 text-primary" />
            <span className="font-heading text-xl font-bold text-white">ShopSwift India</span>
          </div>
          <p className="text-sm">Empowering 10 million+ Indian retailers to go digital</p>
          <p className="text-xs mt-4">© 2025 ShopSwift India. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
