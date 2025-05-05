def print_multilang_result(result):
    if not isinstance(result, dict):
        print(result)
        return

    print("\nResultado:")
    for k, v in result.items():
        if isinstance(v, dict):
            print(f"{k}:")
            for sk, sv in v.items():
                print(f"  - {sk}: {sv}")
        else:
            print(f"{k}: {v}")

    if "messages" in result:
        print("\nMensajes por idioma:")
        for lang, msg in result["messages"].items():
            print(f"  [{lang}]: {msg}")

    if "details" in result:
        print("\nDetalles por idioma:")
        for lang, detail in result["details"].items():
            print(f"  [{lang}]:")
            for dk, dv in detail.items():
                print(f"    {dk}: {dv}")