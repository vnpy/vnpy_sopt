import platform

from setuptools import Extension, setup


def get_ext_modules() -> list:
    """
    获取三方模块
    Linux和Windows需要编译封装接口
    Mac由于缺乏二进制库支持无法使用
    """
    if platform.system() == "Linux":
        extra_compile_flags = [
            "-std=c++17",
            "-O3",
            "-Wno-delete-incomplete",
            "-Wno-sign-compare",
        ]
        extra_link_args = ["-lstdc++"]
        runtime_library_dirs = ["$ORIGIN"]

    elif platform.system() == "Windows":
        extra_compile_flags = ["-O2", "-MT"]
        extra_link_args = []
        runtime_library_dirs = []

    else:
        return

    vnsoptmd = Extension(
        "vnpy_sopt.api.vnsoptmd",
        [
            "vnpy_sopt/api/vnsopt/vnsoptmd/vnsoptmd.cpp",
        ],
        include_dirs=["vnpy_sopt/api/include",
                      "vnpy_sopt/api/vnsopt"],
        define_macros=[],
        undef_macros=[],
        library_dirs=["vnpy_sopt/api/libs", "vnpy_sopt/api"],
        libraries=["soptthostmduserapi_se", "soptthosttraderapi_se"],
        extra_compile_args=extra_compile_flags,
        extra_link_args=extra_link_args,
        runtime_library_dirs=runtime_library_dirs,
        depends=[],
        language="cpp",
    )

    vnsopttd = Extension(
        "vnpy_sopt.api.vnsopttd",
        [
            "vnpy_sopt/api/vnsopt/vnsopttd/vnsopttd.cpp",
        ],
        include_dirs=["vnpy_sopt/api/include",
                      "vnpy_sopt/api/vnsopt"],
        define_macros=[],
        undef_macros=[],
        library_dirs=["vnpy_sopt/api/libs", "vnpy_sopt/api"],
        libraries=["soptthostmduserapi_se", "soptthosttraderapi_se"],
        extra_compile_args=extra_compile_flags,
        extra_link_args=extra_link_args,
        runtime_library_dirs=runtime_library_dirs,
        depends=[],
        language="cpp",
    )

    return [vnsopttd, vnsoptmd]


setup(
    ext_modules=get_ext_modules(),
)
