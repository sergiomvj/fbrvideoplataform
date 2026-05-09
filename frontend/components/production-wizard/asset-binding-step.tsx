"use client";

import { useWizard, type BindingEntry } from "./wizard-state";

export function AssetBindingStep() {
  const { data, setData } = useWizard();
  const template = data.template;

  if (!template) {
    return (
      <div className="text-center py-12">
        <p className="text-sm text-gray-500">No template selected.</p>
      </div>
    );
  }

  const minScenes = (template as unknown as Record<string, unknown>).min_scenes as number | undefined ?? 1;
  const maxScenes = (template as unknown as Record<string, unknown>).max_scenes as number | undefined ?? 1;
  const sceneCount = Math.max(minScenes, 1);

  function ensureBindings(count: number) {
    setData((prev) => {
      const current = prev.bindings ?? [];
      const updated = Array.from({ length: count }, (_, i) =>
        current[i] ?? { sceneIndex: i, assetReference: "", assetType: "image", restrictions: "" }
      );
      return { ...prev, bindings: updated };
    });
  }

  if ((data.bindings ?? []).length !== sceneCount) {
    ensureBindings(sceneCount);
  }

  function updateBinding(index: number, partial: Partial<BindingEntry>) {
    setData((prev) => {
      const updated = [...(prev.bindings ?? [])];
      updated[index] = { ...updated[index], ...partial };
      return { ...prev, bindings: updated };
    });
  }

  const labelClasses = "block text-sm font-medium text-gray-700";
  const inputClasses =
    "block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 placeholder:text-gray-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500";
  const selectClasses =
    "block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500";

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">Asset Binding</h2>
        <p className="text-sm text-gray-500 mt-1">
          Provide asset references and restrictions for each scene ({minScenes}&ndash;{maxScenes} scenes).
        </p>
      </div>

      <div className="space-y-6">
        {(data.bindings ?? []).map((binding, idx) => (
          <div key={idx} className="rounded-lg border border-gray-200 p-4 space-y-4">
            <h3 className="text-sm font-semibold text-gray-800">Scene {idx + 1}</h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label htmlFor={`asset-ref-${idx}`} className={labelClasses}>
                  Asset Reference URL
                </label>
                <input
                  id={`asset-ref-${idx}`}
                  type="url"
                  value={binding.assetReference}
                  onChange={(e) => updateBinding(idx, { assetReference: e.target.value })}
                  placeholder="https://example.com/asset.jpg"
                  className={`${inputClasses} mt-1`}
                />
              </div>

              <div>
                <label htmlFor={`asset-type-${idx}`} className={labelClasses}>
                  Asset Type
                </label>
                <select
                  id={`asset-type-${idx}`}
                  value={binding.assetType}
                  onChange={(e) => updateBinding(idx, { assetType: e.target.value })}
                  className={`${selectClasses} mt-1`}
                >
                  <option value="image">Image</option>
                  <option value="video">Video</option>
                </select>
              </div>
            </div>

            <div>
              <label htmlFor={`restrictions-${idx}`} className={labelClasses}>
                Restrictions (comma-separated)
              </label>
              <input
                id={`restrictions-${idx}`}
                type="text"
                value={binding.restrictions}
                onChange={(e) => updateBinding(idx, { restrictions: e.target.value })}
                placeholder="e.g., no text overlay, landscape only"
                className={`${inputClasses} mt-1`}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
