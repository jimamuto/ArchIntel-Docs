import { Html, Head, Main, NextScript } from 'next/document'

export default function Document() {
    return (
        <Html lang="en" className="bg-[#060608]">
            <Head />
            <body className="bg-[#060608] text-white antialiased">
                <Main />
                <NextScript />
            </body>
        </Html>
    )
}
