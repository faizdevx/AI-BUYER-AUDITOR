import React, { useState, useRef } from 'react';
import type { ProductData } from '../types';
import { Upload } from 'lucide-react';

interface ProductInputProps {
  onAnalyze: (product: ProductData) => void;
  disabled?: boolean;
}

interface PresetItem {
  id: string;
  name: string;
  imageUrl: string;
  rawDetails: string;
}

const PRESETS: PresetItem[] = [
  {
    id: "watch",
    name: "Watch",
    imageUrl: "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&auto=format&fit=crop&q=80",
    rawDetails: `AERO-TITANIUM AUTOMATIC CHRONOGRAPH ($680.00)
Horology / Luxury Hardware

Architectural grade 5 titanium timepiece engineered for extreme durability, lightweight wrist ergonomic feel, and zero-glare readability under direct sunlight.

Key Specifications & Attributes:
- Grade 5 Titanium Solid Case with DLC micro-crystalline coating
- Calibre 9015 Hi-Beat Japanese Automatic Movement (28,800 vph, 42h power reserve)
- Scratch-proof Double-Domed Sapphire Crystal with 5x inner Anti-Reflective coating
- 100M Water Resistance with high-torque screw-down crown
- Swiss Super-LumiNova BGW9 architectural blue lume across dial and hands
- 40mm diameter, 11.2mm thickness, 72g net weight
- 5-Year Global Merchant Warranty with serialized authenticity card (SKU: ATC-G5-BLK-2026)`
  },
  {
    id: "elixir",
    name: "Elixir",
    imageUrl: "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800&auto=format&fit=crop&q=80",
    rawDetails: `MYCO-FOCUS ORGANIC ADAPTOGENIC ELIXIR ($44.00)
Functional Nutrition & Cognitive Biohacking

Potent bio-available dual-extracted mushroom tincture and powder formulated for all-day focus, sustained neuroplasticity, memory retention, and zero afternoon caffeine crash.

Key Specifications & Attributes:
- 100% Organic Lion's Mane, Cordyceps Militaris, and Red Reishi Extract (8:1 concentrated potency)
- Pure fruiting bodies only, zero mycelium on grain or oat starch fillers
- Zero added sugar, vegan, keto-friendly, gluten-free, USDA Organic certified
- Heavy metal, pesticide, and mycotoxin third-party batch laboratory verified
- 150g recyclable amber glass jar / 30 full servings (SKU: MYCO-ADAPT-30S)`
  },
  {
    id: "keyboard",
    name: "Keyboard",
    imageUrl: "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800&auto=format&fit=crop&q=80",
    rawDetails: `ORTHO-SPLIT CNC MECHANICAL KEYBOARD ($295.00)
Developer Hardware & Ergonomics

Columnar staggered split keyboard designed for rapid touch typing, neutral wrist alignment, and zero RSI strain during marathon programming sessions.

Key Specifications & Attributes:
- Solid CNC Anodized 6063 Aerospace Aluminum Split Case
- Hot-swappable Kailh sockets with full QMK/VIA firmware key remapping
- Gasket mounted FR4 switch plate with multi-layer Poron acoustic dampening foam
- Dual USB-C interconnect with ultra-low latency Bluetooth 5.4 multi-device switching
- Per-key south-facing RGB with PBT dye-sublimated cherry profile keycaps
- Dimensions: 280 x 140 x 32 mm per half, weight 880g (SKU: ORTHO-CNC-SPLIT-V2)`
  }
];

export const ProductInput: React.FC<ProductInputProps> = ({ onAnalyze, disabled = false }) => {
  const [productDetails, setProductDetails] = useState(PRESETS[0].rawDetails);
  const [imageUrl, setImageUrl] = useState<string | null>(PRESETS[0].imageUrl);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [productUrl, setProductUrl] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const [selectedPresetId, setSelectedPresetId] = useState<string>(PRESETS[0].id);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const imageReady = Boolean(imageFile);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      const url = URL.createObjectURL(file);
      setImageUrl(url);
      setImageFile(file);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const url = URL.createObjectURL(file);
      setImageUrl(url);
      setImageFile(file);
    }
  };

  const handleSelectPreset = (preset: PresetItem) => {
    setSelectedPresetId(preset.id);
    setProductDetails(preset.rawDetails);
    setImageUrl(preset.imageUrl);
    setImageFile(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const cleanDetails = productDetails.trim() || "MERCHANT PRODUCT DETAIL IN NATURAL LANGUAGE";
    const lines = cleanDetails.split('\n').map(l => l.trim()).filter(Boolean);
    const firstLine = lines[0] || "MERCHANT PRODUCT";
    
    // Extract title
    const title = firstLine.replace(/\(\$?[0-9,.]+\)/g, '').trim() || "MERCHANT PRODUCT";

    const product: ProductData = {
      title: title,
      rawDetails: cleanDetails,
      url: productUrl.trim(),
      description: cleanDetails,
      imageUrl: imageUrl,
      imageFile: imageFile,
      sku: "SKU-" + Math.floor(100000 + Math.random() * 900000),
    };
    onAnalyze(product);
  };

  return (
    <section id="product-input-section" className="relative w-full py-12 sm:py-16 bg-[#0B0F2A] border-b border-navy-700/60">
      <div className="absolute inset-0 bg-grid-tech opacity-20 pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Top Header & Presets */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-6 mb-8 border-b border-navy-700/60">
          <div>
            <span className="text-[11px] font-mono tracking-widest text-crimson uppercase font-bold">
              [ 01 // PRODUCT INGESTION ]
            </span>
            <h2 className="text-2xl sm:text-3xl font-black text-white uppercase tracking-tight mt-1">
              CONFIGURE PRODUCT AUDIT SPEC
            </h2>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <span className="text-[10px] font-mono text-slate-400 tracking-wider uppercase mr-1">
              LOAD DEMO SPEC:
            </span>
            {PRESETS.map((p) => (
              <button
                key={p.id}
                type="button"
                onClick={() => handleSelectPreset(p)}
                className={`px-2.5 py-1 text-[11px] font-mono uppercase border transition-all ${
                  selectedPresetId === p.id
                    ? 'border-posterPink text-posterPink bg-posterPink/10 font-bold'
                    : 'border-navy-700 text-slate-400 hover:border-slate-500 hover:text-white bg-navy-900/80'
                }`}
              >
                {p.name}
              </button>
            ))}
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          <input
            type="url"
            value={productUrl}
            onChange={(event) => setProductUrl(event.target.value)}
            placeholder="Product URL"
            required
            className="w-full bg-navy-950 border border-navy-700 px-4 py-3 text-sm font-mono text-white placeholder:text-slate-500 focus:border-posterPink focus:outline-none"
          />
          
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
            
            {/* LEFT COLUMN: DROP YOUR PRODUCT */}
            <div className="lg:col-span-12 flex flex-col justify-between p-6 sm:p-8 bg-[#0D1038] border border-navy-700 relative group">
              <div className="absolute -top-[1px] -left-[1px] w-2 h-2 bg-crimson" />
              <div className="absolute -bottom-[1px] -right-[1px] w-2 h-2 bg-posterPink" />

              <div>
                <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 tracking-widest uppercase mb-2">
                  <span>SECTION // 01A</span>
                  <span className="text-crimson font-bold">IMAGE DROPZONE</span>
                </div>

                <h3 className="text-3xl sm:text-4xl font-black uppercase text-white tracking-tighter leading-none mb-1">
                  DROP YOUR<br />PRODUCT
                </h3>
                
                <p className="text-xs font-mono text-slate-400 mt-2">
                  Upload a product photo. Drag and drop or browse files.
                </p>
              </div>

              {/* Upload Drop Area */}
              <div className="my-6 flex-1 min-h-[300px] flex flex-col">
                <input 
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="hidden"
                />

                {imageUrl ? (
                  <div className="relative w-full h-full min-h-[280px] flex-1 bg-navy-950 border border-navy-700 flex items-center justify-center overflow-hidden p-2 group/img">
                    <img 
                      src={imageUrl} 
                      alt="Product Preview" 
                      className="w-full h-full object-contain max-h-[300px] transition-transform group-hover/img:scale-105 duration-300"
                    />
                    
                    <div className="absolute inset-0 bg-[#0D1038]/85 opacity-0 group-hover/img:opacity-100 transition-opacity flex flex-col items-center justify-center gap-3 p-4">
                      <p className="text-xs font-mono text-posterPink tracking-widest uppercase font-bold">
                        {imageReady ? 'IMAGE READY FOR VISION VECTOR' : 'UPLOAD IMAGE TO CONTINUE'}
                      </p>
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => fileInputRef.current?.click()}
                          className="px-3 py-1.5 bg-navy-900 border border-slate-500 hover:border-posterPink text-xs font-mono text-white uppercase"
                        >
                          Replace Photo
                        </button>
                        <button
                          type="button"
                          onClick={() => {
                            setImageUrl(null);
                            setImageFile(null);
                          }}
                          className="px-3 py-1.5 bg-crimson/20 border border-crimson hover:bg-crimson text-xs font-mono text-white uppercase"
                        >
                          Remove
                        </button>
                      </div>
                    </div>

                    <div className="absolute top-2 left-2 px-2 py-0.5 bg-navy-950/90 border border-navy-700 text-[10px] font-mono text-posterPink">
                      PREVIEW LOADED
                    </div>
                  </div>
                ) : (
                  <div
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                    onClick={() => fileInputRef.current?.click()}
                    className={`flex-1 w-full min-h-[280px] border-2 border-dashed flex flex-col items-center justify-center p-6 cursor-pointer transition-all ${
                      dragActive 
                        ? 'border-posterPink bg-posterPink/5 scale-[0.99]' 
                        : 'border-navy-600 hover:border-slate-400 bg-navy-950/50'
                    }`}
                  >
                    <div className="w-12 h-12 mb-4 border border-navy-700 flex items-center justify-center text-slate-400 group-hover:text-posterPink group-hover:border-posterPink transition-colors">
                      <Upload className="w-5 h-5" />
                    </div>
                    <p className="text-sm font-mono font-bold text-slate-200 uppercase tracking-wider text-center">
                      CLICK OR DRAG IMAGE HERE
                    </p>
                    <p className="text-[11px] font-mono text-slate-500 mt-1 text-center">
                      PNG, JPG, WEBP UP TO 5MB
                    </p>
                  </div>
                )}
              </div>

              <div className="pt-3 border-t border-navy-700/60 flex items-center justify-between text-[10px] font-mono text-slate-400 uppercase">
                <span>PARSER: OCR / MULTI-MODAL</span>
                <span className={imageReady ? "text-emerald-400 font-bold" : "text-slate-500"}>
                  {imageReady ? "✓ ASSET MOUNTED" : "UPLOAD REQUIRED"}
                </span>
              </div>
            </div>

          </div>

          {/* Main Action Button */}
          <div className="pt-4 flex flex-col sm:flex-row items-center justify-between gap-4 border-t border-navy-700/60">
            <div className="flex items-center gap-3 text-xs font-mono text-slate-400">
              <span className="w-2 h-2 bg-crimson" />
              <span>SIMULATION DURATION: ~10 SECONDS (MULTI-AGENT PROCUREMENT BENCHMARK)</span>
            </div>

            <button
              type="submit"
              disabled={disabled}
              className="w-full sm:w-auto px-8 py-5 bg-crimson hover:bg-posterPink text-white hover:text-navy-950 font-mono text-base font-black tracking-widest uppercase transition-all duration-150 border border-crimson shadow-2xl flex items-center justify-center gap-4 group disabled:opacity-50 disabled:cursor-not-allowed active:translate-y-0.5"
            >
              <span>ANALYZE PRODUCT</span>
              <span className="text-xl font-sans group-hover:translate-x-2 transition-transform duration-150">→</span>
            </button>
          </div>

        </form>

      </div>
    </section>
  );
};