import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { LocationProvider } from "@/contexts/LocationContext";
import { SearchPage } from "./pages/SearchPage";
import { CategoryPage } from "./pages/CategoryPage";
import { ResultsPage } from "./pages/ResultsPage";
import { ProviderDetail } from "./pages/ProviderDetail";
import { LocationError } from "./pages/LocationError";
import { ProviderSignup } from "./pages/ProviderSignup";
import { SignupSuccess } from "./pages/SignupSuccess";
import { AboutPage } from "./pages/AboutPage";
import { ContactPage } from "./pages/ContactPage";
import { PrivacyPolicy } from "./pages/PrivacyPolicy";
import { TermsOfService } from "./pages/TermsOfService";
import NotFound from "./pages/NotFound";
import { OilFilterPage } from "./pages/OilFilterPage";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <LocationProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<SearchPage />} />
            <Route path="/c/:slug" element={<CategoryPage />} />
            <Route path="/results" element={<ResultsPage />} />
            <Route path="/provider/:id" element={<ProviderDetail />} />
            <Route path="/location-error" element={<LocationError />} />
            <Route path="/signup" element={<ProviderSignup />} />
            <Route path="/signup/success" element={<SignupSuccess />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/contact" element={<ContactPage />} />
            <Route path="/legal/privacy" element={<PrivacyPolicy />} />
            <Route path="/legal/terms" element={<TermsOfService />} />
            <Route path="/oil-filter" element={<OilFilterPage />} />
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </LocationProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
