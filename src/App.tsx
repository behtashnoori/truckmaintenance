import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { LocationProvider } from "@/contexts/LocationContext";
import { SessionProvider } from "@/contexts/SessionContext";
import { SessionWarningWrapper } from "@/components/SessionWarningWrapper";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { clearOldCache } from "@/services/categories";
import Index from "./pages/Index";
import { SearchPage } from "./pages/SearchPage";
import { CategoryPage } from "./pages/CategoryPage";
import { CategoryProvidersPage } from "./pages/CategoryProvidersPage";
import { ResultsPage } from "./pages/ResultsPage";
import { ProviderDetail } from "./pages/ProviderDetail";
import { LocationError } from "./pages/LocationError";
import { ProviderSignup } from "./pages/ProviderSignup";
import { SignupSuccess } from "./pages/SignupSuccess";
import { AboutPage } from "./pages/AboutPage";
import { ContactPage } from "./pages/ContactPage";
import { PrivacyPolicy } from "./pages/PrivacyPolicy";
import { TermsOfService } from "./pages/TermsOfService";
import { TestNavigation } from "./pages/TestNavigation";
import AdminLogin from "./pages/AdminLogin";
import AdminDashboard from "./pages/AdminDashboard";
import BusinessExpertDashboard from "./pages/business-expert/BusinessExpertDashboard";
import ApplicationReview from "./pages/business-expert/ApplicationReview";
import { AddProvider } from "./pages/business-expert/AddProvider";
import { BulkUpload } from "./pages/business-expert/BulkUpload";
import { ManageProviders } from "./pages/business-expert/ManageProviders";
import { CategoryManagement } from "./pages/admin/CategoryManagement";
import { LocationsManagement } from "./pages/admin/LocationsManagement";
import { VehicleTypesManagement } from "./pages/admin/VehicleTypesManagement";
import ApplicationsManagement from "./pages/admin/ApplicationsManagement";
import CompaniesManagement from "./pages/admin/CompaniesManagement";
import Reports from "./pages/admin/Reports";
import UsersManagement from "./pages/admin/UsersManagement";
import Settings from "./pages/admin/Settings";
import ContentManagement from "./pages/admin/ContentManagement";
import { ProtectedRoute } from "./components/ProtectedRoute";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

// Clear old cache on app startup
clearOldCache();

const App = () => (
  <ErrorBoundary>
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <LocationProvider>
          <BrowserRouter>
            <SessionProvider>
              <Toaster />
              <Sonner />
              <SessionWarningWrapper />
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/services" element={<SearchPage />} />
            <Route path="/c/:slug" element={<CategoryPage />} />
            <Route path="/category/:slug" element={<CategoryProvidersPage />} />
            <Route path="/results" element={<ResultsPage />} />
            <Route path="/provider/:id" element={<ProviderDetail />} />
            <Route path="/location-error" element={<LocationError />} />
            <Route path="/signup" element={<ProviderSignup />} />
            <Route path="/signup/success" element={<SignupSuccess />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/contact" element={<ContactPage />} />
            <Route path="/legal/privacy" element={<PrivacyPolicy />} />
            <Route path="/legal/terms" element={<TermsOfService />} />
            {/* Test Navigation Route */}
            <Route path="/test-navigation" element={<TestNavigation />} />
            {/* Admin Routes */}
            <Route path="/admin/login" element={<AdminLogin />} />
            <Route path="/admin/dashboard" element={
              <ProtectedRoute requiredRole="admin">
                <AdminDashboard />
              </ProtectedRoute>
            } />
            <Route path="/admin/categories" element={
              <ProtectedRoute requiredRole="admin">
                <CategoryManagement />
              </ProtectedRoute>
            } />
            <Route path="/admin/locations" element={
              <ProtectedRoute requiredRole="admin">
                <LocationsManagement />
              </ProtectedRoute>
            } />
            <Route path="/admin/vehicle-types" element={
              <ProtectedRoute requiredRole="admin">
                <VehicleTypesManagement />
              </ProtectedRoute>
            } />
            <Route path="/admin/applications" element={
              <ProtectedRoute requiredRole="admin">
                <ApplicationsManagement />
              </ProtectedRoute>
            } />
            <Route path="/admin/companies" element={
              <ProtectedRoute requiredRole="admin">
                <CompaniesManagement />
              </ProtectedRoute>
            } />
            <Route path="/admin/reports" element={
              <ProtectedRoute requiredRole="admin">
                <Reports />
              </ProtectedRoute>
            } />
            <Route path="/admin/users" element={
              <ProtectedRoute requiredRole="admin">
                <UsersManagement />
              </ProtectedRoute>
            } />
            <Route path="/admin/settings" element={
              <ProtectedRoute requiredRole="admin">
                <Settings />
              </ProtectedRoute>
            } />
            <Route path="/admin/content" element={
              <ProtectedRoute requiredRole="admin">
                <ContentManagement />
              </ProtectedRoute>
            } />
            {/* Business Expert Routes */}
            <Route path="/business-expert/dashboard" element={
              <ProtectedRoute requiredRole="business_expert">
                <BusinessExpertDashboard />
              </ProtectedRoute>
            } />
            <Route path="/business-expert/applications" element={
              <ProtectedRoute requiredRole="business_expert">
                <ApplicationReview />
              </ProtectedRoute>
            } />
            <Route path="/business-expert/review/:id" element={
              <ProtectedRoute requiredRole="business_expert">
                <ApplicationReview />
              </ProtectedRoute>
            } />
            <Route path="/business-expert/providers" element={
              <ProtectedRoute requiredRole="business_expert">
                <ManageProviders />
              </ProtectedRoute>
            } />
            <Route path="/business-expert/providers/add" element={
              <ProtectedRoute requiredRole="business_expert">
                <AddProvider />
              </ProtectedRoute>
            } />
            <Route path="/business-expert/providers/bulk-upload" element={
              <ProtectedRoute requiredRole="business_expert">
                <BulkUpload />
              </ProtectedRoute>
            } />
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
            </SessionProvider>
          </BrowserRouter>
        </LocationProvider>
      </TooltipProvider>
    </QueryClientProvider>
  </ErrorBoundary>
);

export default App;
