"use client";

import type { FormField as FormFieldType, FormSection } from "@/lib/types";
import { FormField } from "@/components/patient/FormField";

interface RegistryFormProps {
    sections: FormSection[];
    selectedFieldId: string | null;
    onSelectField: (field: FormFieldType) => void;
}

export function RegistryForm({
    sections,
    selectedFieldId,
    onSelectField,
}: RegistryFormProps) {
    return (
        <div className="divide-y divide-slate-200">
            {sections.map((section) => (
                <div key={section.title}>
                    {/* Section header */}
                    <div className="bg-slate-50 px-4 py-2.5">
                        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                            {section.title}
                        </h3>
                    </div>
                    {/* Fields */}
                    <div className="divide-y divide-slate-100">
                        {section.fields.map((field) => (
                            <FormField
                                key={field.id}
                                field={field}
                                isSelected={field.id === selectedFieldId}
                                onSelect={() => onSelectField(field)}
                            />
                        ))}
                    </div>
                </div>
            ))}
        </div>
    );
}
